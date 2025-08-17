# app/services/llm.py
from typing import List
from tenacity import retry, wait_exponential, stop_after_attempt
from app.config import settings

SYSTEM_PROMPT = """You are an assistant that produces structured, concise, and faithful summaries of meeting transcripts.
Follow the user's instruction precisely. If asked to produce bullets, use crisp, scannable points.
Always extract and label: key decisions, action items (with owners and due dates if present), risks/blockers, and next steps when applicable.
Do not invent facts. Prefer quoting or referencing relevant parts of the provided context. If information is missing, state that explicitly."""

def _render_context(chunks: List[str], max_chars: int = 8000) -> str:
    acc = ""
    for i, c in enumerate(chunks):
        part = f"\n\n[Chunk {i+1}]\n{c}"
        if len(acc) + len(part) > max_chars:
            break
        acc += part
    return acc.strip()

def _format_prompt(instruction: str, retrieved_chunks: List[str]) -> str:
    context = _render_context(retrieved_chunks)
    return f"""Context from the transcript:
{context}

User instruction:
{instruction}

Produce the best possible output in a single response, structured and ready to share.
If bullet points are requested, use hyphens. If a section is not applicable, omit it gracefully."""

class LLM:
    def __init__(self):
        self.provider = settings.llm_provider.lower().strip()

        if self.provider == "groq":
            from groq import Groq
            if not settings.groq_api_key:
                raise RuntimeError("GROQ_API_KEY is required for groq provider")
            self.client = Groq(api_key=settings.groq_api_key)
            self.model = "openai/gpt-oss-20b"
        elif self.provider == "mock":
            self.client = None
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
    def generate(self, instruction: str, retrieved_chunks: List[str]) -> str:
        prompt = _format_prompt(instruction, retrieved_chunks)
        if self.provider == "mock":
            return f"[MOCK SUMMARY]\nInstruction: {instruction}\n\nBased on {len(retrieved_chunks)} retrieved chunks:\n- Key points...\n- Action items..."
        # Groq
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1200,
        )
        return resp.choices[0].message.content.strip()
