"""
run_example.py — runs all sample tickets through TicketTriageEnv + the
composite rubric, using a stub "agent" that makes a simple keyword-based
guess at classification (standing in for a real LLM agent). This proves
the whole env -> rubric -> report loop works without any external model
or Foundry credentials, so you can see the pattern before wiring in the
real thing.

Run:
    python run_example.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "rle-template"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "eval-harness"))

from foundry_client import StubFoundryClient  # noqa: E402
from dataset import EvalDataset, EvalRecord  # noqa: E402
from ticket_env import TicketTriageEnv  # noqa: E402
from rubric import build_rubric  # noqa: E402


def stub_agent_guess(ticket: dict) -> dict:
    """
    Extremely naive keyword classifier standing in for a real agent —
    just enough to produce varied, plausible-looking triage decisions so
    the rubric has something real to score. Replace with an actual
    Foundry hosted-agent call for real use.
    """
    text = f"{ticket['subject']} {ticket['body']}".lower()

    if any(w in text for w in ["charge", "refund", "invoice", "billed", "tax"]):
        category = "billing"
    elif any(w in text for w in ["crash", "error", "api", "upload", "500"]):
        category = "technical"
    elif any(w in text for w in ["login", "password", "locked", "2fa", "account"]):
        category = "account"
    else:
        category = "other"

    if any(w in text for w in ["urgent", "production", "down", "demo in an hour"]):
        priority = "urgent"
    elif any(w in text for w in ["can't", "cannot", "locked", "twice"]):
        priority = "high"
    elif category == "other":
        priority = "low"
    else:
        priority = "medium"

    disposition = "escalated" if priority == "urgent" else "resolved"
    action = {
        "category": category,
        "priority": priority,
        "disposition": disposition,
    }
    if disposition == "escalated":
        action["handoff_note"] = f"Customer reports: {ticket['subject']}. Needs immediate attention."

    return action


def main() -> None:
    client = StubFoundryClient(terminal_after=5)
    env = TicketTriageEnv(client=client, rubric=None, max_turns=5)
    dataset = EvalDataset(Path(__file__).parent / "runs" / "example_run.jsonl")

    tickets_path = Path(__file__).parent / "sample_tickets.jsonl"
    with tickets_path.open() as f:
        rows = [json.loads(line) for line in f if line.strip()]

    for i, row in enumerate(rows):
        ticket = row["ticket"]
        ground_truth = row["ground_truth"]

        env.reset(task={"ticket": ticket})
        action = {"type": "triage_decision", "content": stub_agent_guess(ticket)}
        result = env.step(action)

        rubric = build_rubric(ground_truth, call_model=None)
        transcript = env.transcript()
        score = rubric(transcript)
        breakdown = rubric.breakdown(transcript)

        record = EvalRecord(
            episode_id=env.state().episode_id,
            task={"ticket": ticket, "ground_truth": ground_truth},
            transcript=transcript,
            score=score,
            breakdown=breakdown,
            trace_id=env.state().trace_id,
        )
        dataset.append(record)

        guess = action["content"]
        print(
            f"[{i+1:02d}] {ticket['subject']!r:45} "
            f"guess=({guess['category']}, {guess['priority']}) "
            f"truth=({ground_truth['category']}, {ground_truth['priority']}) "
            f"score={score:.2f}"
        )

    print(f"\nMean score across {len(rows)} tickets: {dataset.mean_score():.3f}")
    print("(handoff_note_quality is unscored throughout — no call_model wired up; see rubric.py)")


if __name__ == "__main__":
    main()
