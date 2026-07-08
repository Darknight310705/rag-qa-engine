"""
Generation layer: takes retrieved chunks + the user's query and produces
a grounded answer via the Anthropic API. The system prompt strictly
constrains the model to only use retrieved context and to cite which
chunk(s) support each claim, so we can trace every sentence in the answer
back to a source -- this is what the eval harness's faithfulness check
verifies against.
"""
from typing import List

import anthropic

from src.config import ANTHROPIC_API_KEY, GENERATION_MODEL, MAX_GENERATION_TOKENS
from src.retriever import RetrievedChunk

SYSTEM_PROMPT = """You are a technical Q&A assistant. You must answer the user's \
question using ONLY the provided context chunks below. Do not use outside \
knowledge, even if you are confident it is correct.

Rules:
- Every factual claim in your answer must be traceable to a specific chunk.
- After each claim (or group of claims from the same chunk), cite the chunk \
using its ID in square brackets, e.g. [doc_03::chunk_1].
- If the context does not contain enough information to answer the question, \
say so explicitly rather than guessing.
- Be concise. Do not pad the answer with restated context.
"""


def _format_context(chunks: List[RetrievedChunk]) -> str:
    blocks = []
    for c in chunks:
        blocks.append(f"[{c.chunk_id}]\n{c.text}")
    return "\n\n---\n\n".join(blocks)


def generate_answer(query: str, chunks: List[RetrievedChunk]) -> dict:
    if not chunks:
        return {
            "answer": "I don't have enough retrieved context to answer this question.",
            "sources": [],
        }

    context_block = _format_context(chunks)
    user_message = f"Context:\n\n{context_block}\n\n---\n\nQuestion: {query}"

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=GENERATION_MODEL,
        max_tokens=MAX_GENERATION_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    answer_text = "".join(block.text for block in response.content if block.type == "text")

    return {
        "answer": answer_text,
        "sources": [
            {"chunk_id": c.chunk_id, "doc_id": c.doc_id, "rerank_score": c.rerank_score}
            for c in chunks
        ],
    }
