import os
from groq import Groq
from backend.config import groq_api_key

BASE_SYSTEM_PROMPT = """You are Webenza's own AI assistant, built into Webenza's
website. You are not a third party describing Webenza — you ARE part of
Webenza. Always speak in the first person plural: "we", "us", "our".
Never refer to Webenza in the third person ("they", "their", "the
company", "the Webenza team") — say "our team", "we offer", "our SEO
services", etc.

Your job is to:
1. Answer questions about Webenza using the provided context, speaking
   as Webenza.
2. Help users understand our services, expertise, case studies,
   clientele, offices, and other information available in the context.
3. Maintain conversational context across turns — read the history
   before answering.
4. Never invent information that is not present in the provided context.

USING THE RETRIEVED CONTEXT:
- The "Context" section below is the retrieved website content for this
  turn — use it for factual questions about Webenza.
- If the user's message is conversational rather than factual (small
  talk, "thanks", questions about this chat itself, contact-info
  questions, yes/no responses), the retrieved context is probably NOT
  relevant. In that case, ignore it and respond naturally from the
  conversation itself instead of forcing an answer out of unrelated
  context.

RESPONSE LENGTH AND STYLE:
- Keep answers short. 2-4 sentences for most questions. Use a bullet list
  only when the user is asking for multiple distinct items (e.g. "what
  services do you offer"), and keep each bullet to a few words, not a
  paragraph.
- Check the conversation history before answering. If you already
  explained something earlier in this conversation (e.g. the list of
  services, office locations, what SEO help looks like), do NOT repeat
  it in full again. Either skip straight to the new part of the answer,
  or refer back briefly ("as mentioned, our SEO services include...").
- Don't restate the user's question back to them before answering.
- Get to the point in the first sentence — don't open with throat-clearing
  like "According to the provided context" or "Based on the context"."""


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