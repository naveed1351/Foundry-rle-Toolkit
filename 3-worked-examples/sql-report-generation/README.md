# Worked example: SQL report generation (stub)

**Status: not yet implemented — good first contribution.**

## The intended workflow

An agent receives a natural-language reporting request ("show me revenue by region for Q2") plus a database schema, and must:
1. Generate a SQL query.
2. Execute it (read-only) against the target database.
3. Summarize the result in plain language.

## Why this is a good second example after `support-ticket-triage/`

Unlike ticket triage, correctness here is almost entirely **deterministic and verifiable**: you can execute both the agent's query and a reference query against the same database and compare result sets directly — no LLM judge needed for the core correctness signal. This makes it a good example of the `reference_comparison.py` and `deterministic.py` patterns from `rubric-cookbook/`, and a contrast case to ticket triage's heavier reliance on an LLM judge.

## Suggested shape (following the `support-ticket-triage/` pattern)

- `sql_env.py` — episode = one reporting request. `done` when the agent returns a final summary (not just a query attempt) or fails after N retries.
- `rubric.py` — composite of:
  - **Result-set match** (deterministic): does executing the agent's SQL return the same rows as a reference query, order-independent.
  - **Query safety check** (deterministic): reject/zero-score any query containing `INSERT`/`UPDATE`/`DELETE`/`DROP` — this workflow should be read-only.
  - **Summary faithfulness** (LLM judge, optional): does the plain-language summary accurately reflect the returned data, for cases where result-set match alone doesn't capture summary quality.
- `sample_requests.jsonl` — a handful of (natural-language request, reference SQL, expected result) triples against a small toy schema (e.g. a SQLite file checked into this folder).
- `run_example.py` — same shape as the triage example's runner.

## Want to build this?

This is intentionally left as a stub. If you build it out, please follow the file layout above so the pattern stays consistent across worked examples, and open a PR — see the root `CONTRIBUTING.md`.
