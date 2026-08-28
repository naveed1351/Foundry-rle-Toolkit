"""
Deterministic rubric patterns — verify outcomes with plain code, no model
calls. Prefer these whenever the workflow allows it: cheapest, most
reproducible, no calibration drift over time.

Every rubric here has the signature: (transcript: list[dict]) -> float | None
matching what env.py's `rubric` parameter and eval-harness/ expect.
"""

from __future__ import annotations

import re
from typing import Optional


def task_completed_check(transcript: list[dict]) -> Optional[float]:
    """
    Generic completion check: did the environment ever mark the episode
    terminal in a way that indicates success (not just "ran out of turns")?

    Adapt the `success_markers` set to your workflow's actual terminal
    signal — e.g. a specific tool call name, a status field, a sentinel
    string in the final message.
    """
    success_markers = {"resolved", "completed", "done"}

    for entry in transcript:
        if entry.get("role") != "environment":
            continue
        content = entry.get("content", {})
        status = str(content.get("status", "")).lower()
        if status in success_markers:
            return 1.0

    return 0.0


def regex_match_check(pattern: str):
    """
    Factory: returns a rubric that scores 1.0 if the final agent message
    matches `pattern`, else 0.0. Useful for format-constrained outputs
    (e.g. "final answer must be a JSON object with a 'category' field").
    """
    compiled = re.compile(pattern)

    def rubric(transcript: list[dict]) -> Optional[float]:
        agent_turns = [e for e in transcript if e.get("role") == "agent"]
        if not agent_turns:
            return None
        last_content = str(agent_turns[-1].get("content", ""))
        return 1.0 if compiled.search(last_content) else 0.0

    return rubric


def turn_count_penalty(transcript: list[dict], target_turns: int = 5, penalty_per_extra_turn: float = 0.05) -> Optional[float]:
    """
    Returns a score in [0, 1] that decays as the episode runs longer than
    `target_turns`. Meant to be combined with a task-completion rubric in
    a CompositeRubric (see composite.py) — on its own it can't tell you
    whether the agent actually succeeded, only how efficient it was.
    """
    turn_count = sum(1 for e in transcript if e.get("role") == "agent")
    extra_turns = max(0, turn_count - target_turns)
    return max(0.0, 1.0 - extra_turns * penalty_per_extra_turn)


def schema_conformance_check(required_keys: set[str]):
    """
    Factory: returns a rubric that checks whether the agent's final
    structured output (assumed to be a dict) contains all required keys.
    Useful for workflows like "generate a report with these sections" or
    "classify into one of these categories with a confidence field".
    """

    def rubric(transcript: list[dict]) -> Optional[float]:
        agent_turns = [e for e in transcript if e.get("role") == "agent"]
        if not agent_turns:
            return None
        last_content = agent_turns[-1].get("content", {})
        if not isinstance(last_content, dict):
            return 0.0
        present = required_keys & set(last_content.keys())
        return len(present) / len(required_keys)

    return rubric
