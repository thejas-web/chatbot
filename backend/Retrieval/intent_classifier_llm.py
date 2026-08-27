import json
from groq import Groq
from config import groq_api_key


class LeadSignalClassifier:
    """
    Runs on every user message alongside the main answer generation.

    Determines:
    - whether the visitor shows buying intent
    - whether they declined contact information
    - whether they provided their own contact details
    - whether they explicitly identified their own company
    - what their actual business intent is
    - whether the message needs website/RAG context
    """

    def __init__(self, model: str = "groq/compound-mini"):
        self.client = Groq(api_key=groq_api_key)
        self.model = model

    def analyze(self, latest_message: str, recent_history: list[dict]) -> dict:

        history_text = "\n".join(
            f"{m['role']}: {m['content']}"
            for m in recent_history[-6:]
        )

        system_prompt = """
You are a lead-signal classifier for Webenza's website chatbot.

Your job is to analyze the visitor's LATEST message and return ONLY valid
JSON matching exactly this structure:

{
  "shows_buying_intent": boolean,
  "declines_contact": boolean,
  "extracted_name": string or null,
  "extracted_email": string or null,
  "extracted_phone": string or null,
  "extracted_company": string or null,
  "intent_summary": string or null,
  "needs_context": boolean
}

IMPORTANT EXTRACTION RULES:

1. NAME

Extract a name only when the visitor explicitly provides or identifies
their own name.

Examples:

"My name is John"
→ extracted_name = "John"

"I'm John"
→ extracted_name = "John"

"John here"
→ extracted_name = "John"

Do NOT extract names of:
- Webenza employees
- clients
- people mentioned in website content
- people mentioned in the visitor's question

If the visitor does not explicitly identify a name as their own:
→ extracted_name = null


2. EMAIL

Extract an email only when the visitor provides their own email address.

Examples:

"my email is john@gmail.com"
→ extracted_email = "john@gmail.com"

"You can reach me at john@gmail.com"
→ extracted_email = "john@gmail.com"

Do NOT extract an email address merely because it appears in:
- website content
- retrieved context
- conversation history
- an example mentioned by the visitor

Only the LATEST message may provide a new extracted value.


3. PHONE

Extract a phone number only when the visitor provides their own phone
number or clearly says it is their contact number.

Examples:

"my number is 9876543210"
→ extracted_phone = "9876543210"

"You can call me on 9876543210"
→ extracted_phone = "9876543210"

Do NOT extract phone numbers mentioned in:
- website content
- examples
- retrieved context
- unrelated discussion


4. COMPANY — VERY IMPORTANT

Extract a company ONLY when the visitor explicitly identifies that
company as THEIR OWN company, employer, business, organization, or
workplace.

Valid examples:

"I work at ABC Technologies"
→ extracted_company = "ABC Technologies"

"My company is ABC"
→ extracted_company = "ABC"

"I run an ecommerce business called ABC"
→ extracted_company = "ABC"

"I am from ABC"
→ extracted_company = "ABC"

"I own ABC"
→ extracted_company = "ABC"


INVALID examples:

"What kind of company is Webenza?"
→ extracted_company = null

"What services does Webenza provide?"
→ extracted_company = null

"Tell me about Brigade Group"
→ extracted_company = null

"Does Webenza work with ABC?"
→ extracted_company = null

"Is ABC a client of Webenza?"
→ extracted_company = null

"I need SEO for my ecommerce business"
→ extracted_company = null
unless the visitor actually gives the business/company name.

The mere presence of a company name in the message does NOT mean it is
the visitor's company.

When uncertain:
→ extracted_company = null


5. BUYING INTENT

Set shows_buying_intent = true when the visitor demonstrates an intention
to potentially purchase or engage Webenza's services.

Examples:

"I need SEO for my website"
→ true

"We need help with digital marketing"
→ true

"How much do your SEO services cost?"
→ true

"Can someone contact me?"
→ true

"I'd like a proposal"
→ true

"Can I schedule a call?"
→ true

"I am looking for an agency to handle our PPC"
→ true

Normal informational questions are NOT automatically buying intent.

Examples:

"Where is Webenza located?"
→ false

"What services does Webenza offer?"
→ false

"Who are your clients?"
→ false

"What is Webenza?"
→ false

"Tell me about your SEO services"
→ false unless the message indicates an intention
to purchase, engage, or request help.


6. INTENT SUMMARY

When shows_buying_intent = true, create a SHORT summary of what the
visitor wants from Webenza.

The summary should describe the visitor's business need, NOT simply
repeat their message.

Examples:

"I need SEO for my ecommerce website"
→ "Interested in SEO services for an ecommerce website"

"We need someone to manage our Google Ads"
→ "Interested in PPC/Google Ads management"

"Can someone contact me about improving our website traffic?"
→ "Interested in improving website traffic and discussing Webenza's services"

"I'd like a proposal for digital marketing"
→ "Interested in a digital marketing proposal"

When there is NO buying intent:
→ intent_summary = null

Do NOT use personal-information messages as the intent.

Example:

"my email is john@gmail.com"
→ intent_summary = null

"My number is 9876543210"
→ intent_summary = null


7. DECLINING CONTACT

Set declines_contact = true if the visitor explicitly refuses to provide
contact information.

Examples:

"No thanks"
"I don't want to share my number"
"I'd rather not"
"Just browsing"
"Don't contact me"

Otherwise:
→ false


8. NEEDS_CONTEXT

Set needs_context = true only when answering the latest message requires
factual information about Webenza from its website.

Examples requiring context:

"Where is Webenza located?"
"What services do you offer?"
"Who are your clients?"
"Tell me about your SEO services"

Set needs_context = false for:

"Hi"
"Thanks"
"Okay"
"Sure"
"Why do you need my email?"
"Don't contact me"
"my email is john@gmail.com"
"my name is John"

IMPORTANT:

Use the conversation history only to understand the meaning of the latest
message.

DO NOT extract name, email, phone, or company from conversation history.
Those values must be explicitly present in the LATEST message.

Return ONLY JSON.
Do not include markdown.
Do not include explanations.
Do not include ```json.
"""

        user_prompt = (
            f"Recent conversation:\n"
            f"{history_text}\n\n"
            f"LATEST VISITOR MESSAGE:\n"
            f"{latest_message}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0,
                max_tokens=300,
            )

            raw = response.choices[0].message.content.strip()
            print("\n========== LEAD CLASSIFIER RAW RESPONSE ==========")
            print(repr(raw))
            print("==================================================\n")
            # Safety cleanup in case the model still wraps JSON
            if raw.startswith("```json"):
                raw = raw[7:]

            if raw.startswith("```"):
                raw = raw[3:]

            if raw.endswith("```"):
                raw = raw[:-3]

            raw = raw.strip()

            result = json.loads(raw)

            return result

        except Exception as e:
            print(f"Error during lead signal classification: {e}")

            # Fail safe
            return {
                "shows_buying_intent": False,
                "declines_contact": False,
                "extracted_name": None,
                "extracted_email": None,
                "extracted_phone": None,
                "extracted_company": None,
                "intent_summary": None,
                "needs_context": True,
            }