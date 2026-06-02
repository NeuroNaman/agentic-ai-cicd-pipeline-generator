"""Tests for the Validation Agent."""

from __future__ import annotations

import pytest

from src.agents.validation import ValidationAgent
from src.models import (
    GeneratedFile,
    PipelineConfig,
    PipelineState,
    ValidationSeverity,
)


@pytest.fixture
def valid_github_actions_yaml() -> str:
    """Valid GitHub Actions workflow YAML."""
    return """
name: CI/CD Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  ci:
    name: CI - Build & Test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
"""


@pytest.fixture
def invalid_yaml() -> str:
    """Invalid YAML content."""
    return """
name: Bad Pipeline
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Step with neither uses nor run
        env:
          FOO: bar
"""


@pytest.fixture
def yaml_with_secrets() -> str:
    """YAML with hardcoded secrets."""
    return """
name: Insecure Pipeline
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: echo "deploying"
        env:
          API_KEY: "sk-1234567890abcdef"
          password: "supersecret123"
"""


class TestValidationAgent:
    """Tests for ValidationAgent."""

    @pytest.mark.asyncio
    async def test_valid_pipeline_passes(self, valid_github_actions_yaml: str):
        """Test that a valid pipeline passes validation."""
        agent = ValidationAgent()
        state = PipelineState(
            generated_pipeline=PipelineConfig(
                platform="github_actions",
                files=[GeneratedFile(
                    path=".github/workflows/ci.yml",
                    content=valid_github_actions_yaml,
                    description="CI pipeline",
                    is_primary=True,
                )],
            ),
        )

        result = await agent.execute(state)
        assert result.validation_report is not None
        assert result.validation_report.passed
        assert result.validation_report.syntax_valid
        assert result.validation_report.semantic_valid

    @pytest.mark.asyncio
    async def test_invalid_yaml_fails_syntax(self):
        """Test that invalid YAML fails syntax validation."""
        agent = ValidationAgent()
        state = PipelineState(
            generated_pipeline=PipelineConfig(
                platform="github_actions",
                files=[GeneratedFile(
                    path=".github/workflows/ci.yml",
                    content="invalid: yaml: content: [unclosed",
                    description="Bad pipeline",
                    is_primary=True,
                )],
            ),
        )

        result = await agent.execute(state)
        report = result.validation_report
        assert report is not None
        assert not report.passed
        assert not report.syntax_valid

    @pytest.mark.asyncio
    async def test_missing_steps_fails_semantic(self, invalid_yaml: str):
        """Test that a step without uses/run fails semantic validation."""
        agent = ValidationAgent()
        state = PipelineState(
            generated_pipeline=PipelineConfig(
                platform="github_actions",
                files=[GeneratedFile(
                    path=".github/workflows/ci.yml",
                    content=invalid_yaml,
                    description="Invalid pipeline",
                    is_primary=True,
                )],
            ),
        )

        result = await agent.execute(state)
        report = result.validation_report
        assert report is not None

        semantic_errors = [i for i in report.issues if i.category == "semantic"]
        assert any("neither 'uses' nor 'run'" in i.message for i in semantic_errors)

    @pytest.mark.asyncio
    async def test_hardcoded_secrets_detected(self, yaml_with_secrets: str):
        """Test that hardcoded secrets are detected."""
        agent = ValidationAgent()
        state = PipelineState(
            generated_pipeline=PipelineConfig(
                platform="github_actions",
                files=[GeneratedFile(
                    path=".github/workflows/ci.yml",
                    content=yaml_with_secrets,
                    description="Insecure pipeline",
                    is_primary=True,
                )],
            ),
        )

        result = await agent.execute(state)
        report = result.validation_report
        assert report is not None

        security_issues = [i for i in report.issues if i.category == "security"]
        assert len(security_issues) > 0
        assert any(i.severity == ValidationSeverity.ERROR for i in security_issues)
