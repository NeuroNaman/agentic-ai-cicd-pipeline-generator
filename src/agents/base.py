"""Base agent class — standard interface for all agents in the system."""

from __future__ import annotations

import abc
import time
from typing import Any, Generic, TypeVar

import structlog

from src.models import PipelineState

logger = structlog.get_logger()

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseAgent(abc.ABC, Generic[InputT, OutputT]):
    """
    Abstract base class for all agents in the Agentic CI/CD system.

    Every agent follows the Plan → Act → Observe → Reflect loop:
    1. Plan: Determine what needs to be done based on current state
    2. Act: Execute tools/LLM calls to perform the task
    3. Observe: Collect results and update state
    4. Reflect: Evaluate results and decide if task is complete

    Agents are stateless — all state is passed via PipelineState.
    """

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self._logger = logger.bind(agent=name)

    @abc.abstractmethod
    async def execute(self, state: PipelineState) -> PipelineState:
        """
        Execute the agent's primary task.

        Args:
            state: Current pipeline state.

        Returns:
            Updated pipeline state.
        """
        ...

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        LangGraph-compatible callable interface.

        Converts dict state to PipelineState, executes, and converts back.
        """
        pipeline_state = PipelineState(**state)

        self._logger.info(
            "agent_started",
            stage=pipeline_state.current_stage,
            repo=pipeline_state.repo_url,
        )

        start_time = time.monotonic()
        try:
            updated_state = await self.execute(pipeline_state)
            duration = time.monotonic() - start_time

            self._logger.info(
                "agent_completed",
                duration_seconds=round(duration, 2),
                stage=updated_state.current_stage,
            )

            updated_state.execution_logs.append(
                f"[{self.name}] Completed in {duration:.2f}s"
            )

            return updated_state.model_dump()

        except Exception as e:
            duration = time.monotonic() - start_time
            self._logger.error(
                "agent_failed",
                error=str(e),
                duration_seconds=round(duration, 2),
            )
            pipeline_state.execution_logs.append(
                f"[{self.name}] FAILED after {duration:.2f}s: {e}"
            )
            raise

    def _log(self, event: str, **kwargs: Any) -> None:
        """Structured logging helper."""
        self._logger.info(event, **kwargs)
