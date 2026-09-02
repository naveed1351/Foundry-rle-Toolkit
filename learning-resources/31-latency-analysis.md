# Analyze Latency by Stage

Question: Where does time accumulate in an agent run?

Practice: Break latency into model, retrieval, tool, queue, retry, and evaluator spans.

Evidence: Percentiles for each stage, not just end-to-end average.

Avoid: Tuning prompts for latency while a downstream tool is slow.
