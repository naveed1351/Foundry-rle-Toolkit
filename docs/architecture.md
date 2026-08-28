# Architecture

How the pieces in this toolkit map onto Microsoft Foundry's hill-climbing loop.

```
                         ┌─────────────────────────────────────────┐
                         │            YOUR WORKFLOW                 │
                         │  (support triage, report gen, etc.)      │
                         └───────────────────┬───────────────────────┘
                                             │  codify
                                             ▼
                         ┌─────────────────────────────────────────┐
                         │        rle-template/  (this repo)         │
                         │  reset()  → start a fresh task instance   │
                         │  step()   → agent acts, env responds      │
                         │  state()  → current status + trace ref    │
                         └───────────────────┬───────────────────────┘
                                             │  runs inside
                                             ▼
                    ┌────────────────────────────────────────────────┐
                    │   Foundry hosted agent (per-session ACA sandbox) │
                    │   harness + Microsoft Agent Framework + model     │
                    └───────────────────┬────────────────────────────┘
                                        │  every run traced (OpenTelemetry)
                                        ▼
                    ┌────────────────────────────────────────────────┐
                    │           eval-harness/                          │
                    │   trace → eval dataset → rubric score            │
                    │   (rubric patterns in rubric-cookbook/)           │
                    └───────────────────┬────────────────────────────┘
                                        │  scored runs
                        ┌───────────────┴───────────────┐
                        ▼                                 ▼
        ┌───────────────────────────┐      ┌───────────────────────────────┐
        │   NON-PARAMETRIC LEARNING   │      │   PARAMETRIC LEARNING           │
        │   Agent Optimizer / SkillOpt│      │   Frontier Tuning (RFT)         │
        │   tunes prompts, tools,     │      │   via Tinker + ECHO on OpenEnv  │
        │   model choice — no weight  │      │   — retrains model weights      │
        │   changes                   │      │   when the economics justify it │
        └───────────────┬─────────────┘      └────────────────┬────────────────┘
                        │                                     │
                        └──────────────┬──────────────────────┘
                                       ▼
                         ┌─────────────────────────────┐
                         │  Deploy the improved agent    │
                         │  Teams / M365 Copilot / any    │
                         │  other channel                 │
                         └─────────────────────────────┘

         See optimizer-vs-finetune-decision-guide/ for choosing between
         the two learning branches above.
```

## Component responsibilities

- **`rle-template/`** — the only piece that talks OpenEnv. It wraps a Foundry hosted agent so any OpenEnv-compatible trainer or runtime can drive it without custom integration code.
- **`rubric-cookbook/`** — pure logic, no Foundry dependency. Rubrics are plain functions that take a trace/transcript and return a score. Kept separate so you can unit-test and iterate on them fast.
- **`eval-harness/`** — the glue between Foundry's trace output and a rubric. Pulls traces, applies a rubric, and accumulates an eval dataset you can point Agent Optimizer or a fine-tuning job at.
- **`3-worked-examples/`** — full vertical slices combining all of the above for a realistic workflow, so you have something to copy instead of starting from an empty template.

## Design principles

1. **The rubric is the product.** Everything else in this toolkit is plumbing to get a trustworthy score attached to every run. Spend your time on the rubric, not the wrapper code.
2. **Start non-parametric.** Agent Optimizer / SkillOpt changes are cheap and reversible — exhaust that before considering fine-tuning.
3. **Keep the model swappable.** Don't hardcode a specific model's quirks into your rubric or environment — the loop, not the model, is the durable asset.
4. **Traces are ground truth.** If your rubric and your traces disagree, trust the trace and fix the rubric.
