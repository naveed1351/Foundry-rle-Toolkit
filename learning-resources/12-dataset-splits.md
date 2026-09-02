# Keep Dataset Splits Honest

Question: Which cases guide iteration and which cases guard against overfitting?

Practice: Freeze a held-out set before tuning and prevent near-duplicates across splits.

Evidence: Split counts, provenance, and duplicate-detection results.

Avoid: Repeatedly inspecting held-out failures until they become training examples.
