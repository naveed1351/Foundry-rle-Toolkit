"""
FoundryAgentEnv — a minimal OpenEnv-compatible wrapper around a Microsoft
Foundry hosted agent.

This class does not run the agent itself. It adapts an existing Foundry
hosted-agent session to the OpenEnv `reset / step / state` contract so any
OpenEnv-compatible trainer, evaluator, or Agent Optimizer run can drive it
without custom integration code.

Fill in the TODOs to point this at your real workflow. The stub client in
`foundry_client.py` is a fake in-memory agent so you can validate the
contract shape before wiring in real Foundry SDK calls.
"""

from __future__ import annotations

import dataclasses
import time
import uuid
from typing import Any, Callable, Optional

from foundry_client import FoundryClient


@dataclasses.dataclass
class StepResult:
    """Return value of env.step(). Mirrors the OpenEnv step contract."""

    observation: dict
    reward: Optional[float]
    done: bool
    info: dict


@dataclasses.dataclass
class EnvState:
    """Return value of env.state()."""

    episode_id: str
    turn_count: int
    done: bool
    trace_id: Optional[str]


class FoundryAgentEnv:
    """
    OpenEnv-compatible wrapper around a Foundry hosted agent.

    Parameters
    ----------
    client:
        A FoundryClient (or your own compatible client) that knows how to
        start a session, send a message, and fetch trace metadata.
    rubric:
        A callable ``(transcript: list[dict]) -> float | None`` that scores
        the episode so far. Pass ``None`` to disable online scoring and rely
        entirely on offline scoring in eval-harness/. See rubric-cookbook/
        for ready-made patterns.
    max_turns:
        Safety cap so a stuck agent can't loop forever during optimization
        runs. Tune per workflow.
    """

    def __init__(
        self,
        client: FoundryClient,
        rubric: Optional[Callable[[list[dict]], Optional[float]]] = None,
        max_turns: int = 20,
    ):
        self.client = client
        self.rubric = rubric
        self.max_turns = max_turns

        self._episode_id: Optional[str] = None
        self._session_id: Optional[str] = None
        self._transcript: list[dict] = []
        self._turn_count = 0
        self._done = False

    def reset(self, task: Optional[dict] = None) -> dict:
        """
        Start a fresh episode.

        `task` carries whatever your workflow needs to define one episode:
        e.g. {"ticket_id": "..."} for support triage, or
        {"question": "...", "dataset": "..."} for report generation.

        TODO: replace the placeholder task payload with your workflow's
        real task-sampling logic (pull from a dataset, a queue, etc).
        """
        self._episode_id = str(uuid.uuid4())
        self._turn_count = 0
        self._done = False
        self._transcript = []

        task = task or {"prompt": "Describe the task here."}

        self._session_id = self.client.start_session(
            agent_id=self.client.agent_id,
            metadata={"episode_id": self._episode_id, "task": task},
        )

        initial_observation = {
            "episode_id": self._episode_id,
            "task": task,
        }
        self._transcript.append({"role": "system", "content": task})
        return initial_observation

    def step(self, action: dict) -> StepResult:
        """
        Advance the environment by one turn.

        `action` is whatever the agent produced this turn — typically a
        dict like {"type": "message", "content": "..."} or
        {"type": "tool_call", "name": "...", "arguments": {...}}.

        TODO: replace the placeholder completion logic with a real call
        through self.client to your Foundry hosted agent, and replace the
        `done` heuristic with your workflow's actual termination condition.
        """
        if self._done:
            raise RuntimeError("step() called after episode was done — call reset() first.")

        self._turn_count += 1
        self._transcript.append({"role": "agent", "content": action})

        response = self.client.send_message(self._session_id, action)
        self._transcript.append({"role": "environment", "content": response})

        done = response.get("terminal", False) or self._turn_count >= self.max_turns

        reward = None
        if self.rubric is not None:
            reward = self.rubric(self._transcript)

        self._done = done

        observation = {
            "episode_id": self._episode_id,
            "turn": self._turn_count,
            "response": response,
        }
        info = {
            "trace_id": self.client.get_trace_id(self._session_id),
            "turn_count": self._turn_count,
            "timestamp": time.time(),
        }

        return StepResult(observation=observation, reward=reward, done=done, info=info)

    def state(self) -> EnvState:
        """Return current status without advancing the episode."""
        trace_id = None
        if self._session_id is not None:
            trace_id = self.client.get_trace_id(self._session_id)

        return EnvState(
            episode_id=self._episode_id or "",
            turn_count=self._turn_count,
            done=self._done,
            trace_id=trace_id,
        )

    def transcript(self) -> list[dict]:
        """Full transcript for this episode — used by eval-harness/ and rubrics."""
        return list(self._transcript)
