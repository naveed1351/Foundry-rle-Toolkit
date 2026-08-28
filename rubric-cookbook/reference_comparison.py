"""
Reference-comparison rubric patterns — score against a known-good answer.
Use when your eval/training data includes a "gold" reference for each task
(common for classification, extraction, and report-generation workflows
where you have historical human-produced examples).
"""

from __future__ import annotations

import difflib
from typing import Optional


def exact_match(reference: str):
    """Strict equality after whitespace normalization. Use for categorical outputs."""

    def rubric(transcript: list[dict]) -> Optional[float]:
        final = _final_agent_text(transcript)
        if final is None:
            return None
        return 1.0 if final.strip().lower() == reference.strip().lower() else 0.0

    return rubric


def fuzzy_match(reference: str, threshold: float = 0.85):
    """
    Similarity ratio via difflib (no extra dependencies). Good enough for
    short structured outputs; for long free-text prefer embedding
    similarity or an LLM judge instead — string similarity penalizes
    valid paraphrases heavily.
    """

    def rubric(transcript: list[dict]) -> Optional[float]:
        final = _final_agent_text(transcript)
        if final is None:
            return None
        ratio = difflib.SequenceMatcher(None, final.strip().lower(), reference.strip().lower()).ratio()
        return ratio if ratio >= threshold else ratio * 0.5  # partial credit, weighted down

    return rubric


def embedding_similarity(reference: str, embed_fn, threshold: float = 0.8):
    """
    Cosine similarity between the agent's final answer and a reference,
    using whatever embedding function you provide (Foundry Models catalog,
    OpenAI, sentence-transformers, etc — kept generic on purpose).

    `embed_fn` signature: (text: str) -> list[float]

    This is the right default for long free-text answers where exact or
    fuzzy string match is too brittle but you still have a reference.
    """
    import math

    reference_vec = embed_fn(reference)

    def cosine(a: list[float], b: list[float]) -> float:
        if len(a) != len(b):
            raise ValueError(
                "Embedding vectors must have the same dimension; "
                f"got {len(a)} and {len(b)}."
            )
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def rubric(transcript: list[dict]) -> Optional[float]:
        final = _final_agent_text(transcript)
        if final is None:
            return None
        final_vec = embed_fn(final)
        sim = max(0.0, min(1.0, cosine(final_vec, reference_vec)))
        return sim if sim >= threshold else sim * 0.7

    return rubric


def _final_agent_text(transcript: list[dict]) -> Optional[str]:
    agent_turns = [e for e in transcript if e.get("role") == "agent"]
    if not agent_turns:
        return None
    content = agent_turns[-1].get("content", "")
    if isinstance(content, dict):
        content = content.get("content", "")
    return str(content)
