"""
Composite rubric for the support-ticket-triage example. Combines
deterministic checks against labeled ground truth with an LLM-judge check
for handoff-note quality on escalated tickets.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "rubric-cookbook"))

from composite import CompositeRubric  # noqa: E402


def _final_action_content(transcript: list[dict]) -> Optional[dict]:
    """
    Transcript entries store the whole action the agent sent, e.g.
    {"role": "agent", "content": {"type": "triage_decision", "content": {...}}}
    — the actual triage decision is one level further in, under the
    action's own "content" key. Unwrap that here so every rubric
    component in this file works from the flat decision dict.
    """
    agent_turns = [e for e in transcript if e.get("role") == "agent"]
    if not agent_turns:
        return None
    action = agent_turns[-1].get("content", {})
    if not isinstance(action, dict):
        return None
    decision = action.get("content", action)  # unwrap if present, else assume already flat
    return decision if isinstance(decision, dict) else None


def make_category_correctness(ground_truth_category: str):
    def category_correctness(transcript: list[dict]) -> Optional[float]:
        content = _final_action_content(transcript)
        if content is None:
            return None
        return 1.0 if content.get("category") == ground_truth_category else 0.0

    return category_correctness


def make_priority_correctness(ground_truth_priority: str):
    def priority_correctness(transcript: list[dict]) -> Optional[float]:
        content = _final_action_content(transcript)
        if content is None:
            return None
        return 1.0 if content.get("priority") == ground_truth_priority else 0.0

    return priority_correctness


def turn_efficiency(transcript: list[dict], target_turns: int = 2) -> Optional[float]:
    turn_count = sum(1 for e in transcript if e.get("role") == "agent")
    extra = max(0, turn_count - target_turns)
    return max(0.0, 1.0 - extra * 0.15)


def make_handoff_note_quality(call_model=None):
    """
    LLM-judge component for escalated tickets only. If `call_model` is
    None (e.g. running the smoke test with no model access), this
    component always returns None and is excluded from the composite via
    require_all=False rather than distorting the score with a guess.
    """

    def handoff_note_quality(transcript: list[dict]) -> Optional[float]:
        content = _final_action_content(transcript)
        if content is None or content.get("disposition") != "escalated":
            return None  # not applicable to resolved tickets
        if call_model is None:
            return None  # no model wired up — see rubric-cookbook/llm_judge.py

        note = content.get("handoff_note", "")
        if not note.strip():
            return 0.0

        # In a real setup: from llm_judge import llm_judge; delegate to it here.
        raise NotImplementedError("Wire call_model through rubric-cookbook/llm_judge.py")

    return handoff_note_quality


def build_rubric(ground_truth: dict, call_model=None) -> CompositeRubric:
    """
    ground_truth: {"category": "...", "priority": "..."} for this specific ticket.
    """
    return CompositeRubric(
        components=[
            (make_category_correctness(ground_truth["category"]), 0.4),
            (make_priority_correctness(ground_truth["priority"]), 0.2),
            (make_handoff_note_quality(call_model), 0.3),
            (turn_efficiency, 0.1),
        ],
        require_all=False,
    )
