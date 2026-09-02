# Specify Terminal States

Question: When is an episode complete, failed, or safely abandoned?

Practice: Add explicit terminal reasons such as success, policy violation, timeout, and exhausted budget.

Evidence: Episode summaries grouped by terminal reason.

Avoid: Ending every run only on timeout; it hides workflow defects behind latency.
