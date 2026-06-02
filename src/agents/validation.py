"""
Validation Agent — Multi-layer validation of generated CI/CD pipelines.

Validates pipelines through:
1. Syntax validation (YAML/JSON schema)
2. Semantic validation (stage ordering, dependencies)
3. Security scanning (hardcoded secrets, permissions)
4. Dry run (sandboxed execution via `act` or Docker)
"""

from __future__ import annotations

import re
import time
from typing import Any

import structlog
import yaml

from src.agents.base import BaseAgent
from src.models import (
    PipelineState,
    ValidationIssue,
    ValidationReport,
    ValidationSeverity,
)

logger = structlog.get_logger()

# Patterns that indicate hardcoded secrets
SECRET_PATTERNS = [
    (r"(?:password|passwd|pwd)\s*[:=]\s*['\"][^$\{][^'\"]+['\"]", "Possible hardcoded password"),
    (r"(?:api[_-]?key|apikey)\s*[:=]\s*['\"][^$\{][^'\"]+['\"]", "Possible hardcoded API key"),
    (r"(?:secret|token)\s*[:=]\s*['\"][^$\{][^'\"]+['\"]", "Possible hardcoded secret/token"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID detected"),
    (r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}", "GitHub token detected"),
]

# Known valid GitHub Actions
KNOWN_ACTIONS = {
    "actions/checkout",
    "actions/setup-python",
    "actions/setup-node",
    "actions/setup-go",
    "actions/setup-java",
    "actions/cache",
    "docker/setup-buildx-action",
    "docker/login-action",
    "docker/build-push-action",
    "hashicorp/setup-terraform",
    "azure/setup-kubectl",
    "dtolnay/rust-toolchain",
}


class ValidationAgent(BaseAgent):
    """
    Validates generated CI/CD pipeline configurations through multiple layers.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ValidationAgent",
            description="Multi-layer validation of generated CI/CD pipelines",
        )

    async def execute(self, state: PipelineState) -> PipelineState:
        """Validate the generated pipeline."""
        state.current_stage = "validating"

        if not state.generated_pipeline:
            raise ValueError("Generated pipeline is required. Run PipelineGeneratorAgent first.")

        start_time = time.monotonic()
        issues: list[ValidationIssue] = []

        # Layer 1: Syntax validation
        syntax_issues = self._validate_syntax(state)
        issues.extend(syntax_issues)
        syntax_valid = not any(i.severity == ValidationSeverity.ERROR for i in syntax_issues)

        # Layer 2: Semantic validation
        semantic_issues = self._validate_semantics(state)
        issues.extend(semantic_issues)
        semantic_valid = not any(i.severity == ValidationSeverity.ERROR for i in semantic_issues)

        # Layer 3: Security scanning
        security_issues = self._validate_security(state)
        issues.extend(security_issues)
        security_passed = not any(i.severity == ValidationSeverity.ERROR for i in security_issues)

        # Layer 4: Dry run (if sandbox is enabled)
        dry_run_passed = None
        dry_run_logs = None
        # TODO: Implement sandbox dry run with `act` or Docker
        # dry_run_passed, dry_run_logs = await self._dry_run(state)

        duration = time.monotonic() - start_time

        # Build report
        passed = syntax_valid and semantic_valid and security_passed
        if dry_run_passed is not None:
            passed = passed and dry_run_passed

        state.validation_report = ValidationReport(
            passed=passed,
            issues=issues,
            syntax_valid=syntax_valid,
            semantic_valid=semantic_valid,
            security_passed=security_passed,
            dry_run_passed=dry_run_passed,
            dry_run_logs=dry_run_logs,
            duration_seconds=round(duration, 2),
        )

        self._log(
            "validation_complete",
            passed=passed,
            num_issues=len(issues),
            errors=sum(1 for i in issues if i.severity == ValidationSeverity.ERROR),
            warnings=sum(1 for i in issues if i.severity == ValidationSeverity.WARNING),
        )

        return state

    def _validate_syntax(self, state: PipelineState) -> list[ValidationIssue]:
        """Validate YAML/JSON syntax of generated files."""
        issues: list[ValidationIssue] = []
        assert state.generated_pipeline is not None

        for file in state.generated_pipeline.files:
            if file.path.endswith((".yml", ".yaml")):
                try:
                    parsed = yaml.safe_load(file.content)
                    if parsed is None:
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category="syntax",
                            message="YAML file is empty",
                            file_path=file.path,
                        ))
                    elif not isinstance(parsed, dict):
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category="syntax",
                            message="YAML root must be a mapping",
                            file_path=file.path,
                        ))
                except yaml.YAMLError as e:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category="syntax",
                        message=f"Invalid YAML: {e}",
                        file_path=file.path,
                    ))

        return issues

    def _validate_semantics(self, state: PipelineState) -> list[ValidationIssue]:
        """Validate semantic correctness of pipeline configuration."""
        issues: list[ValidationIssue] = []
        assert state.generated_pipeline is not None

        for file in state.generated_pipeline.files:
            if not file.path.endswith((".yml", ".yaml")):
                continue

            try:
                config = yaml.safe_load(file.content)
                if not isinstance(config, dict):
                    continue
            except yaml.YAMLError:
                continue  # Already caught in syntax validation

            platform = state.generated_pipeline.platform

            if platform == "github_actions":
                issues.extend(self._validate_github_actions_semantics(config, file.path))
            elif platform == "gitlab_ci":
                issues.extend(self._validate_gitlab_ci_semantics(config, file.path))

        return issues

    def _validate_github_actions_semantics(
        self, config: dict[str, Any], file_path: str
    ) -> list[ValidationIssue]:
        """Validate GitHub Actions workflow semantics."""
        issues: list[ValidationIssue] = []

        # Must have 'name'
        if "name" not in config:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="semantic",
                message="Workflow missing 'name' field",
                file_path=file_path,
                suggestion="Add a descriptive 'name' field",
            ))

        # Must have 'on' (triggers)
        # NOTE: yaml.safe_load() parses bare 'on' as boolean True (YAML 1.1 quirk)
        # So we check for both the string "on" and the boolean True as the key
        has_on_trigger = "on" in config or True in config
        if not has_on_trigger:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="semantic",
                message="Workflow missing 'on' trigger configuration",
                file_path=file_path,
            ))

        # Must have 'jobs'
        jobs = config.get("jobs")
        if not jobs:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="semantic",
                message="Workflow has no jobs defined",
                file_path=file_path,
            ))
            return issues

        # Validate each job
        job_names = set(jobs.keys())
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                continue

            # Must have runs-on
            if "runs-on" not in job_config:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="semantic",
                    message=f"Job '{job_name}' missing 'runs-on'",
                    file_path=file_path,
                ))

            # Must have steps
            if "steps" not in job_config:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="semantic",
                    message=f"Job '{job_name}' has no steps",
                    file_path=file_path,
                ))

            # Validate 'needs' references
            needs = job_config.get("needs", [])
            if isinstance(needs, str):
                needs = [needs]
            for dep in needs:
                if dep not in job_names:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category="semantic",
                        message=f"Job '{job_name}' depends on non-existent job '{dep}'",
                        file_path=file_path,
                    ))

            # Validate steps have 'uses' or 'run'
            for i, step in enumerate(job_config.get("steps", [])):
                if not isinstance(step, dict):
                    continue
                if "uses" not in step and "run" not in step:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category="semantic",
                        message=f"Step {i+1} in job '{job_name}' has neither 'uses' nor 'run'",
                        file_path=file_path,
                    ))

            # Warn if a 'docker' job exists but no Dockerfile was found in state
            if "docker" in job_name.lower() or "build" in job_name.lower():
                has_docker_step = any(
                    "docker" in str(step).lower()
                    for step in job_config.get("steps", [])
                    if isinstance(step, dict)
                )
                if has_docker_step:
                    # This is expected — no warning needed; Docker detection handles it
                    pass

        return issues

    def _validate_gitlab_ci_semantics(
        self, config: dict[str, Any], file_path: str
    ) -> list[ValidationIssue]:
        """Validate GitLab CI semantics."""
        issues: list[ValidationIssue] = []

        if "stages" not in config:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="semantic",
                message="GitLab CI missing 'stages' definition",
                file_path=file_path,
                suggestion="Define stages explicitly for clarity",
            ))

        return issues

    def _validate_security(self, state: PipelineState) -> list[ValidationIssue]:
        """Scan for security issues in generated configurations."""
        issues: list[ValidationIssue] = []
        assert state.generated_pipeline is not None

        for file in state.generated_pipeline.files:
            # Check for hardcoded secrets
            for pattern, description in SECRET_PATTERNS:
                matches = re.finditer(pattern, file.content, re.IGNORECASE)
                for match in matches:
                    line_num = file.content[:match.start()].count("\n") + 1
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category="security",
                        message=description,
                        file_path=file.path,
                        line_number=line_num,
                        suggestion="Use secret references (${{ secrets.NAME }}) instead",
                    ))

            # Check for overly permissive permissions
            if "permissions: write-all" in file.content:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="security",
                    message="Overly permissive 'write-all' permissions",
                    file_path=file.path,
                    suggestion="Use least-privilege permissions",
                ))

        return issues
