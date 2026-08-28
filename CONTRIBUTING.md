# Contributing

This is a community learning resource, not an official Microsoft project. Contributions that make the pattern clearer or more complete are very welcome.

## Highest-value contributions

1. **Fill in the stub worked examples** (`3-worked-examples/sql-report-generation/`, `3-worked-examples/document-classification/`) — each has a suggested shape in its README. Follow the file layout established in `3-worked-examples/support-ticket-triage/` so the pattern stays consistent.
2. **New rubric patterns** in `rubric-cookbook/` — if you've built a rubric shape that doesn't fit the four existing patterns (deterministic, reference-comparison, LLM-judge, composite), it's probably useful to others too.
3. **Real (anonymized) case studies** — if you've taken a workflow through this pattern at your org, the before/after numbers (score deltas, cost deltas from Agent Optimizer or Frontier Tuning) are the single most valuable thing you can contribute. Add it as a new folder under `3-worked-examples/` or as a write-up linked from the root README.
4. **A .NET port** — this toolkit is Python-first, but Foundry's SDKs have parity across languages. A `dotnet/` sibling to `rle-template/` following the same `reset/step/state` contract would help a lot of teams.

## Ground rules

- **Keep the OpenEnv contract intact.** `reset`, `step`, `state` are the load-bearing methods — don't add methods that bypass them or change their signatures in ways that break OpenEnv compatibility.
- **No secrets, no real customer data.** All sample data in this repo (tickets, documents, requests) must be synthetic or clearly anonymized. Do not upload real logs, real trace exports, or real credentials — even in an example.
- **Test before you PR.** Every example should have a `run_example.py` (or equivalent) that runs standalone against the stub Foundry client, with zero external credentials required, so contributors and reviewers can verify it works without Azure access. Run it yourself before opening the PR.
- **Keep the stub-first pattern.** New environments and examples should default to `StubFoundryClient` so they're runnable out of the box; real-Foundry wiring goes behind a clearly marked TODO, following the existing `rle-template/foundry_client.py` structure.
- **Cite sources for any Microsoft Foundry claims.** This space moves fast — if you reference a specific feature, cost number, or API behavior, link to the Microsoft doc or blog post it came from so readers can verify it's still current.

## Filing issues

Bug reports, broken examples, and "this doesn't match current Foundry docs" reports are all welcome as GitHub issues — Foundry's API surface is evolving quickly and this repo will drift out of date without people flagging it.

## Code style

- Python 3.10+, type hints on public functions.
- No hard dependency beyond the standard library at the `rle-template/` and `rubric-cookbook/` level — keep those two folders framework-agnostic so people can adopt the pattern without buying into a specific stack.
- Docstrings that explain *why*, not just *what* — this repo's value is the teaching, not just working code.
