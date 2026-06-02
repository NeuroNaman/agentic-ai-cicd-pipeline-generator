"""
Self-Healing Agent — Diagnoses and fixes pipeline failures automatically.

Analyzes execution logs, classifies errors, determines root cause,
generates fixes, and retries the pipeline.
"""

from __future__ import annotations

import re
from typing import Any

import structlog

from src.agents.base import BaseAgent
from src.models import (
    ErrorCategory,
    ErrorRecord,
    HealingAction,
    PipelineState,
)

logger = structlog.get_logger()

# ==============================================================================
# Error classification patterns
# ==============================================================================
ERROR_PATTERNS: dict[ErrorCategory, list[str]] = {
    ErrorCategory.DEPENDENCY: [
        r"ModuleNotFoundError",
        r"ImportError",
        r"Cannot find module",
        r"Package .+ not found",
        r"No matching distribution found",
        r"Could not resolve dependencies",
        r"npm ERR! 404",
        r"go: module .+ not found",
        r"cargo: package .+ not found",
    ],
    ErrorCategory.CONFIGURATION: [
        r"yaml\.scanner\.ScannerError",
        r"SyntaxError",
        r"Invalid configuration",
        r"Missing required field",
        r"Unknown key",
        r"Error: .+ is not a valid",
    ],
    ErrorCategory.PERMISSION: [
        r"Permission denied",
        r"EACCES",
        r"403 Forbidden",
        r"401 Unauthorized",
        r"Access denied",
        r"insufficient permissions",
    ],
    ErrorCategory.INFRASTRUCTURE: [
        r"Connection refused",
        r"Cannot connect to",
        r"Service unavailable",
        r"503 Service Temporarily Unavailable",
        r"infrastructure error",
        r"cluster not found",
    ],
    ErrorCategory.RESOURCE_LIMIT: [
        r"Out of memory",
        r"OOMKilled",
        r"Disk quota exceeded",
        r"No space left on device",
        r"Resource limit",
        r"quota exceeded",
    ],
    ErrorCategory.TEST_FAILURE: [
        r"FAILED",
        r"assertion error",
        r"AssertionError",
        r"test.*failed",
        r"Expected .+ but got",
        r"\d+ failed, \d+ passed",
    ],
    ErrorCategory.TIMEOUT: [
        r"timeout",
        r"Timed out",
        r"deadline exceeded",
        r"Task exceeded maximum time",
    ],
    ErrorCategory.NETWORK: [
        r"ETIMEDOUT",
        r"ECONNREFUSED",
        r"DNS resolution failed",
        r"Network unreachable",
        r"SSL certificate",
        r"fetch failed",
    ],
    ErrorCategory.BUILD_FAILURE: [
        r"Build failed",
        r"Compilation error",
        r"Error: Command failed",
        r"exit code [1-9]",
        r"make: \*\*\*.*Error",
    ],
    ErrorCategory.DEPLOYMENT_FAILURE: [
        r"Deployment failed",
        r"rollout failed",
        r"health check failed",
        r"Container .+ exited with",
        r"CrashLoopBackOff",
    ],
}


class SelfHealingAgent(BaseAgent):
    """
    Analyzes pipeline failures and generates fixes.

    Flow: Parse logs → Classify error → Analyze root cause → Generate fix
    """

    def __init__(self) -> None:
        super().__init__(
            name="SelfHealingAgent",
            description="Diagnoses and fixes CI/CD pipeline failures",
        )

    async def execute(self, state: PipelineState) -> PipelineState:
        """Diagnose and fix pipeline failure."""
        state.current_stage = "healing"
        state.retry_count += 1

        # Get error context
        error_logs = self._get_error_logs(state)
        if not error_logs:
            self._log("no_error_logs", message="No error logs found to diagnose")
            return state

        # Step 1: Classify the error
        category = self._classify_error(error_logs)

        # Step 2: Extract root cause
        root_cause = self._analyze_root_cause(error_logs, category)

        # Step 3: Generate fix
        healing_action = await self._generate_fix(state, error_logs, category, root_cause)

        # Step 4: Record the error
        error_record = ErrorRecord(
            error_message=error_logs[:500],
            category=category,
            root_cause=root_cause,
            fix_applied=healing_action.description if healing_action else None,
        )
        state.error_history.append(error_record)

        # Step 5: Apply fix to generated pipeline
        if healing_action and healing_action.changes:
            assert state.generated_pipeline is not None
            for change in healing_action.changes:
                # Find and replace the matching file
                for i, existing_file in enumerate(state.generated_pipeline.files):
                    if existing_file.path == change.path:
                        state.generated_pipeline.files[i] = change
                        break
                else:
                    state.generated_pipeline.files.append(change)

        self._log(
            "healing_complete",
            category=category.value,
            root_cause=root_cause,
            fix_applied=healing_action.description if healing_action else "No fix generated",
            retry_count=state.retry_count,
        )

        return state

    def _get_error_logs(self, state: PipelineState) -> str:
        """Extract error logs from state."""
        logs = []

        if state.execution_result and state.execution_result.logs:
            logs.append(state.execution_result.logs)

        if state.execution_result and state.execution_result.error_message:
            logs.append(state.execution_result.error_message)

        if state.validation_report and state.validation_report.dry_run_logs:
            logs.append(state.validation_report.dry_run_logs)

        # Also include validation issues
        if state.validation_report:
            for issue in state.validation_report.issues:
                logs.append(f"[{issue.severity.value}] {issue.category}: {issue.message}")

        return "\n".join(logs)

    def _classify_error(self, error_logs: str) -> ErrorCategory:
        """Classify the error based on log patterns."""
        scores: dict[ErrorCategory, int] = {}

        for category, patterns in ERROR_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, error_logs, re.IGNORECASE)
                score += len(matches)
            if score > 0:
                scores[category] = score

        if not scores:
            return ErrorCategory.UNKNOWN

        return max(scores, key=lambda k: scores[k])

    def _analyze_root_cause(self, error_logs: str, category: ErrorCategory) -> str:
        """Analyze root cause from error logs."""
        # For now, use pattern matching. In production, this would use LLM.
        cause_lines = []

        for line in error_logs.splitlines():
            line = line.strip()
            if not line:
                continue

            # Look for lines that indicate the cause
            if any(indicator in line.lower() for indicator in [
                "error:", "failed:", "fatal:", "exception:",
                "caused by:", "reason:", "because",
            ]):
                cause_lines.append(line)

        if cause_lines:
            return "; ".join(cause_lines[:3])

        return f"Unresolved {category.value} error"

    async def _generate_fix(
        self,
        state: PipelineState,
        error_logs: str,
        category: ErrorCategory,
        root_cause: str,
    ) -> HealingAction | None:
        """
        Generate a fix for the identified error.

        In production, this would use LLM with RAG context to generate fixes.
        For now, uses heuristic-based fixes.
        """
        # TODO: Implement LLM-powered fix generation
        # The LLM would receive:
        # - Error logs
        # - Error category
        # - Root cause analysis
        # - Current pipeline config
        # - Repository analysis
        # - Similar historical fixes from knowledge base

        self._log(
            "generating_fix",
            category=category.value,
            root_cause=root_cause,
        )

        # Placeholder: return a description of what would be fixed
        return HealingAction(
            description=f"Fix {category.value} error: {root_cause}",
            category=category,
            confidence=0.7,
            reasoning=f"Based on error pattern analysis: {root_cause}",
        )
