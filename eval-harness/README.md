# eval-harness

Wires Foundry traces to rubrics from `rubric-cookbook/`, and accumulates the results into an eval dataset — the thing you point Agent Optimizer or a fine-tuning job at.

Without this piece, your rubric only ever sees one transcript at a time inside a live `step()` call. This harness is what turns a stream of individual scored runs into a **dataset**: something you can slice, aggregate, regression-test against, and hand to Foundry's optimization tooling.

## Files

- `dataset.py` — `EvalDataset`: append-only store of `(task, transcript, score, breakdown, metadata)` records, with basic slicing/aggregation helpers. Backed by a local JSONL file by default — swap for a real store (Azure Blob, a database) once you outgrow that.
- `collect.py` — pulls a batch of episodes (from `rle-template/`'s `FoundryAgentEnv`, or directly from Foundry trace export) and scores each with a rubric, appending to an `EvalDataset`.
- `report.py` — quick aggregate stats and regressions: mean score, score distribution, worst-N transcripts to eyeball, and a diff against a previous dataset snapshot (did the last Agent Optimizer run actually help?).

## Typical loop

```bash
# 1. Run a batch of episodes and score them
python collect.py --episodes 50 --rubric ../3-worked-examples/support-ticket-triage/rubric.py --out runs/2026-08-28.jsonl

# 2. Look at the results
python report.py runs/2026-08-28.jsonl

# 3. After an Agent Optimizer run, compare before/after
python report.py runs/2026-08-28.jsonl --compare runs/2026-08-29-post-optimize.jsonl
```

## Why local JSONL first

It's tempting to reach straight for a database or a cloud store. Don't — a flat JSONL file is enough to validate your rubric and your collection loop, is trivially diffable in git for small datasets, and costs you nothing to throw away and restart when you inevitably revise your rubric (see rubric-cookbook's "version your rubrics" rule). Move to a real store only once the dataset is large enough or shared enough that JSONL stops being convenient.
