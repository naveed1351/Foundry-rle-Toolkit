# Foundry RLE Toolkit

**Turn an existing Microsoft Foundry agent harness into an OpenEnv-compatible Reinforcement Learning Environment (RLE) — so it can be scored, optimized, and eventually fine-tuned, instead of hand-tweaked forever.**

> Status: early / community accelerator. Built against Microsoft Foundry's June–July 2026 "hill-climbing loop" announcement (hosted agents + Toolboxes + Memory + Agent Optimizer + OpenEnv + Frontier Tuning). Not an official Microsoft project.

## The problem this solves

Microsoft Foundry now supports a full "practice → judge → learn" loop for agents:

1. **Practice** — a hosted agent (your harness + Microsoft Agent Framework + a swappable model) runs inside a per-session Azure Container Apps sandbox.
2. **Judge** — every run is traced; a rubric you define scores the outcome.
3. **Learn** — Agent Optimizer / SkillOpt tune prompts, tools, and model choice (no weight changes); or, when the economics justify it, Foundry post-training (Tinker + ECHO) fine-tunes the weights via the OpenEnv standard.

The `reset / step / state` contract that OpenEnv requires is simple. **What's genuinely hard — and currently undocumented in practice — is turning a real business workflow into a well-posed RLE**: deciding what a "step" is, writing a rubric that actually captures the outcome you care about, and wiring traces into an eval dataset. Every team is currently reinventing this from scratch.

This toolkit is a reference pattern + starter kit for that conversion, not a wrapper around the Foundry SDK itself.

## What's here

| Folder | What it teaches |
|---|---|
| [`rle-template/`](./rle-template) | Minimal OpenEnv-compliant wrapper around a Foundry hosted agent. Copy this as your starting point. |
| [`rubric-cookbook/`](./rubric-cookbook) | Patterns for turning fuzzy outcomes into deterministic or LLM-judged reward functions. The hardest part, so it gets the most attention. |
| [`3-worked-examples/`](./3-worked-examples) | Three realistic workflows taken end-to-end: harness → RLE → Agent Optimizer run → before/after eval scores. |
| [`optimizer-vs-finetune-decision-guide/`](./optimizer-vs-finetune-decision-guide) | When to stop at non-parametric tuning vs. invest in Frontier Tuning / RFT, with real cost/quality numbers. |
| [`eval-harness/`](./eval-harness) | Wiring OpenTelemetry traces → eval dataset → rubric, so the loop is observable, not a black box. |
| [`docs/`](./docs) | Background reading, glossary, architecture diagram. |

## Quickstart

```bash
git clone https://github.com/<you>/foundry-rle-toolkit
cd foundry-rle-toolkit/rle-template
pip install -r requirements.txt -r ../eval-harness/requirements.txt
cp .env.example .env   # fill in your Foundry project + agent IDs
python run_smoke_test.py
```

This runs one `reset()` → `step()` → `state()` cycle against a stub agent so you can confirm the contract works before you plug in real logic.

## Learning path

1. Read [`docs/glossary.md`](./docs/glossary.md) if terms like "RLE", "hill-climbing loop", or "non-parametric vs parametric" are new.
2. Read [`docs/architecture.md`](./docs/architecture.md) for the full diagram of how these pieces connect.
3. Copy `rle-template/` and get the smoke test passing against your own hosted agent.
4. Read `rubric-cookbook/README.md` and pick the closest pattern to your workflow.
5. Walk through the worked example closest to your use case in `3-worked-examples/`.
6. Wire up `eval-harness/` so your traces become a growing eval dataset.
7. Use `optimizer-vs-finetune-decision-guide/` to decide your next move.

## Contributing

New worked examples, rubric patterns, and language ports (this is Python-first; a .NET port would be very welcome given Foundry's SDK parity) are all welcome — see [`CONTRIBUTING.md`](./CONTRIBUTING.md). If you productionize this at your org, an anonymized case study in `3-worked-examples/` is the single most valuable contribution you can make.

## Disclaimer

This is a community learning resource, not official Microsoft guidance. Foundry's Agent Optimizer, OpenEnv integration, and Frontier Tuning are recent (some preview) features — APIs referenced here may drift. Always check the [Microsoft Foundry blog](https://devblogs.microsoft.com/foundry/) and [Foundry docs](https://learn.microsoft.com/en-us/azure/foundry/) for current behavior before relying on this in production.
