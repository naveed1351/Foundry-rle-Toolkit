# Worked example: support ticket triage

An end-to-end walkthrough turning a support-ticket-triage agent harness into an RLE, scoring it, and running it through the optimize loop.

## The workflow

The agent receives a support ticket (subject, body, customer tier) and must:
1. Classify it into one of a fixed set of categories (`billing`, `technical`, `account`, `other`).
2. Assign a priority (`low`, `medium`, `high`, `urgent`).
3. Either resolve it directly with a templated response, or escalate to a human with a one-sentence handoff note.

This is a good first example because the episode is short (usually 1-3 turns), the outcome is mostly checkable by code, and it still needs an LLM-judge component for the parts a script can't verify (is the handoff note actually useful).

## Files

- `ticket_env.py` — subclasses `FoundryAgentEnv` from `rle-template/`, defining what a ticket-triage episode looks like: `reset(task={"ticket": {...}})`, and a `done` condition of "agent either resolved or escalated." (Named `ticket_env.py`, not `env.py`, to avoid a module-name collision with `rle-template/env.py` when both are imported.)
- `rubric.py` — a `CompositeRubric` combining:
  - **Category correctness** (deterministic, 0.4 weight) — does the assigned category match the labeled ground truth in the sample dataset.
  - **Priority correctness** (deterministic, 0.2 weight) — same, for priority.
  - **Handoff note quality** (LLM judge, 0.3 weight) — only applies when the agent escalated; scores whether the note would actually help a human pick up the ticket without re-reading it.
  - **Turn efficiency** (deterministic, 0.1 weight) — penalizes unnecessary back-and-forth.
- `sample_tickets.jsonl` — 12 synthetic labeled tickets to run the smoke test against. Replace with real (anonymized) historical tickets before using this for anything beyond learning the pattern.
- `run_example.py` — runs all 12 sample tickets through the env + rubric and prints a report, so you can see the whole loop work end-to-end without any Foundry credentials.

## Run it

```bash
pip install -r ../../rle-template/requirements.txt
python run_example.py
```

Expected output: a per-ticket score breakdown and an aggregate report, using the stub Foundry client so this runs with zero external dependencies. Swap in `RealFoundryClient` (see `rle-template/foundry_client.py`) once you're ready to point this at a real hosted agent.

## What to change for your own workflow

1. Replace `sample_tickets.jsonl` with your own labeled data — even 20-30 real examples beats synthetic ones for calibrating the LLM-judge component.
2. Adjust the category/priority sets in `env.py` and `rubric.py` to match your actual taxonomy.
3. Recalibrate the composite weights in `rubric.py` — the 0.4/0.2/0.3/0.1 split here is a reasonable starting point, not a universal constant. If escalation quality matters more to you than raw classification accuracy, shift weight toward the LLM-judge component.
