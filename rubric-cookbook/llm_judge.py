"""
LLM-judge rubric pattern — for qualitative outcomes with no reference
answer (helpfulness, tone, whether free-form reasoning is sound). Highest
cost and lowest reliability of the four patterns in this cookbook: use
only when deterministic or reference-comparison rubrics genuinely don't
apply, and calibrate against human labels before trusting the scores (see
README.md rules of thumb).

`call_model` is intentionally left generic — plug in a Foundry Models
catalog call, or any other chat-completions-style client. Keeping the
judge model decoupled from your agent's model is deliberate: never reuse
the same model instance/conversation for both, or you risk the agent's
own reasoning leaking into the judge's context.
"""

from __future__ import annotations

import json
import re
from typing import Callable, Optional

JUDGE_SYSTEM_PROMPT = """You are an evaluator scoring a single completed \
agent conversation. You did not participate in the conversation and have \
no stake in a high or low score — score strictly against the rubric \
below and nothing else.

Rubric criteria:
{criteria}

Respond with ONLY a JSON object of the form:
{{"score": <float between 0 and 1>, "reasoning": "<one sentence>"}}
"""


def llm_judge(
    call_model: Callable[[str, str], str],
    criteria: str,
    model_name: str = "judge-model",
):
    """
    Factory: returns a rubric that asks a separate model to score the
    transcript against `criteria`.

    Parameters
    ----------
    call_model:
        Callable(system_prompt, user_prompt) -> raw text response.
        Wire this to your actual model client.
    criteria:
        Plain-language description of what a good outcome looks like.
        Be specific — vague criteria produce noisy, uncalibrated scores.
        Example: "The agent correctly identified the customer's issue,
        proposed a solution consistent with company policy, and did not
        make promises the company can't keep."
    """
    system_prompt = JUDGE_SYSTEM_PROMPT.format(criteria=criteria)

    def rubric(transcript: list[dict]) -> Optional[float]:
        transcript_text = _render_transcript(transcript)
        if not transcript_text.strip():
            return None

        raw_response = call_model(system_prompt, transcript_text)
        parsed = _extract_json(raw_response)
        if parsed is None or "score" not in parsed:
            # Judge failed to return parseable output — don't guess, mark unscored.
            return None

        score = float(parsed["score"])
        return max(0.0, min(1.0, score))

    return rubric


def _render_transcript(transcript: list[dict]) -> str:
    lines = []
    for entry in transcript:
        role = entry.get("role", "unknown")
        content = entry.get("content", "")
        lines.append(f"[{role}] {content}")
    return "\n".join(lines)


def _extract_json(text: str) -> Optional[dict]:
    """Best-effort JSON extraction in case the judge wraps output in prose or fences."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
