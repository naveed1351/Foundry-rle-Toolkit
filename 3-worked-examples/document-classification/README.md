# Worked example: document classification (stub)

**Status: not yet implemented — good first contribution.**

## The intended workflow

An agent receives a document (contract, invoice, resume, etc.) and must classify it into a taxonomy, extract a handful of key fields, and flag low-confidence cases for human review rather than guessing.

## Why this is a good third example

It's a good contrast to the other two worked examples:
- Unlike `support-ticket-triage/`, there's no "escalation note" to judge qualitatively — this is almost purely a `schema_conformance_check` + `exact_match`/`fuzzy_match` pattern from `rubric-cookbook/`.
- Unlike `sql-report-generation/`, correctness isn't verifiable by re-executing anything — you need labeled ground truth for both the classification and the extracted fields.
- It's a good place to demonstrate the **"unscored, not wrong" pattern**: the rubric should specifically reward correctly flagging low-confidence documents for human review, not just penalize wrong answers — an agent that says "I'm not sure" on a genuinely ambiguous document should score *better* than one that confidently guesses wrong.

## Suggested shape (following the `support-ticket-triage/` pattern)

- `doc_env.py` — episode = one document. `done` when the agent returns a classification + extracted fields, or an explicit "needs human review" flag.
- `rubric.py` — composite of:
  - **Classification correctness** (deterministic, against labeled ground truth).
  - **Field extraction accuracy** (deterministic, using `schema_conformance_check` plus per-field `exact_match`/`fuzzy_match`).
  - **Appropriate abstention** (deterministic): reward the agent for flagging genuinely ambiguous documents instead of guessing — this needs a labeled "ambiguity" flag in your ground truth data.
- `sample_documents.jsonl` — a handful of labeled synthetic documents (short enough to embed as text, no real PII).
- `run_example.py` — same shape as the triage example's runner.

## Want to build this?

This is intentionally left as a stub. If you build it out, please follow the file layout above so the pattern stays consistent across worked examples, and open a PR — see the root `CONTRIBUTING.md`.
