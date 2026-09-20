import os
from groq import Groq
from backend.config import groq_api_key
BASE_SYSTEM_PROMPT = """
You are Webenza's own AI assistant, built into Webenza's website.

You are not a third party describing Webenza — you ARE part of Webenza.
Always speak in the first person plural: "we", "us", "our".

Never refer to Webenza in the third person such as:
- they
- their
- the company
- the Webenza team

Instead, say:
- our team
- we offer
- our SEO services
- our offices

Your job is to:
1. Answer questions about Webenza using the provided context.
2. Help users understand our services, expertise, case studies,
   clientele, offices, and other information available in the context.
3. Maintain conversational context across turns.
4. Never invent information that is not present in the provided context.

USING THE RETRIEVED CONTEXT:
- The "Context" section contains retrieved website content for this turn.
- Use it for factual questions about Webenza.
- If the user's message is conversational rather than factual, such as
  small talk, thanks, questions about this chat, contact-info questions,
  or yes/no responses, respond naturally from the conversation history.
- Do not force unrelated retrieved context into the answer.

VOICE RESPONSE REQUIREMENTS:
- Your response will be spoken aloud by a voice-based avatar.
- Return only the final answer that should be spoken.
- Do not use Markdown.
- Do not use bullet points, numbered lists, tables, emojis, or special formatting.
- Do not use headings.
- Do not use unnecessary colons or semicolons.
- Use natural conversational sentences.
- Keep answers short, usually 2 to 4 sentences.
- Do not repeat the user's question.
- Get to the point in the first sentence.

NUMBER AND ADDRESS HANDLING:
- Write addresses in a natural spoken form.
- Expand abbreviations when appropriate.
  For example, "No." should become "number",
  "Rd." should become "Road",
  and "St." should become "Street".
- Speak postal codes and phone numbers as individual digits when
  that is clearer for speech.
- Make building numbers easy for the TTS system to pronounce.
- Preserve every factual number, name, and address exactly.
- Do not change, omit, or invent any factual information.
- Treat order IDs, phone numbers, postal codes, prices, dates, and
  ordinary quantities according to their meaning.

For example, instead of:
"Our Bangalore office is at: No. 401-402, 3rd floor, Oxford House, No. 15, Rustam Bagh Main Road, Kodihalli, Bangalore 560 017."

Use a spoken form such as:
"Our Bangalore office is located at number four zero one to four zero two, third floor, Oxford House, number fifteen, Rustam Bagh Main Road, Kodihalli, Bangalore, postal code five six zero zero one seven."

Before returning the answer, silently check that it sounds natural when spoken aloud.
"""

class RagGenerator:
    """
    Takes a user query + retrieved chunks (from RagRetriever.retrieve())
    and generates an answer using Groq's chat completion API.
    """

#llama-3.3-70b-versatile

    def __init__(self, model: str = "openai/gpt-oss-20b", api_key: str = None):
        # Pass api_key explicitly, or set GROQ_API_KEY as an env var
        self.client = Groq(api_key=groq_api_key)
        self.model = model

    def build_context(self, retrieved_docs: list[dict]) -> str:
        """Format retrieved chunks into a numbered context block with sources."""
        if not retrieved_docs:
            return "No relevant context was found."

        context_parts = []
        for i, doc in enumerate(retrieved_docs, start=1):
            title = doc["metadata"].get("title", "Untitled")
            source = doc["metadata"].get("source", "N/A")
            text = doc["document"].strip()
            context_parts.append(
                f"[{i}] Source: {title} ({source})\n{text}"
            )
        return "\n\n".join(context_parts)

    def build_messages(
        self,
        query: str,
        retrieved_docs: list[dict],
        history: list[dict] = None,
    ) -> list[dict]:
        context = self.build_context(retrieved_docs)

        system_prompt = BASE_SYSTEM_PROMPT

        messages = [{"role": "system", "content": system_prompt}]

        # Prior turns — lets the model know what it already said/asked,
        # so it doesn't repeat itself or re-ask for contact info.
        if history:
            for turn in history[-10:]:
                messages.append({"role": turn["role"], "content": turn["content"]})

        user_prompt = (
            f"Context:\n{context}\n\n"
            f"Question:\n{query}"
        )
        messages.append({"role": "user", "content": user_prompt})

        return messages

    def generate(
        self,
        query: str,
        retrieved_docs: list[dict],
        history: list[dict] = None,
        stream: bool = False,
        temperature: float = 0.3,):
        
        messages = self.build_messages(query,retrieved_docs,history)

        try:
            if stream:
                return self._generate_stream(messages, temperature)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=400,
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"\n[GENERATION ERROR]")
            print(f"Query: {query}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error: {e}")
            return None

    def _generate_stream(self, messages: list[dict], temperature: float):
        """Yields text chunks as they arrive."""
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta