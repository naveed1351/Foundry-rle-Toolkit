# Control Episode Budgets

Question: How much model, tool, and wall-clock budget may one task consume?

Practice: Set per-episode limits and expose budget exhaustion as a terminal state.

Evidence: Token, request, tool-call, and elapsed-time distributions.

Avoid: Optimizing quality on unconstrained runs that cannot operate economically.
