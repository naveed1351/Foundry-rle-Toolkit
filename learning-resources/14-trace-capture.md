# Capture Decision-Useful Traces

Question: Can a failed score be traced to an observation, action, tool result, and terminal state?

Practice: Correlate each episode with stable IDs and record model, prompt, tools, and latency.

Evidence: One trace that can reconstruct an evaluation outcome end to end.

Avoid: Logging only final text, which prevents diagnosis and replay.
