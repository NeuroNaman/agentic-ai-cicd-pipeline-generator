"""Tests for the Pipeline Generator Agent."""

from __future__ import annotations

import yaml
import pytest

from src.agents.pipeline_generator import PipelineGeneratorAgent
from src.agents.planner import PlannerAgent
from src.agents.repo_analysis import RepoAnalysisAgent
from src.models import PipelineState

import tempfile
from pathlib import Path


@pytest.fixture
def python_repo_state() -> PipelineState:
    """Create a state with analyzed Python repo and plan."""
    temp_dir = tempfile.mkdtemp(prefix="test_gen_")

    files = {
        "app.py": 'from fastapi import FastAPI\napp = FastAPI()\n',
        "requirements.txt": "fastapi==0.115.0\nuvicorn==0.30.0\n",
        "tests/test_app.py": "def test_example():\n    assert True\n",
        "Dockerfile": "FROM python:3.12-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"uvicorn\", \"app:app\"]\n",
    }

    for filepath, content in files.items():
        full_path = Path(temp_dir) / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    return PipelineState(
        repo_url="https://github.com/test/python-app",
        repo_local_path=temp_dir,
    )


class TestPipelineGeneratorAgent:
    """Tests for PipelineGeneratorAgent."""

    @pytest.mark.asyncio
    async def test_full_generation_flow(self, python_repo_state: PipelineState):
        """Test the full flow: analysis → planning → generation."""
        # Step 1: Analyze
        repo_agent = RepoAnalysisAgent()
        state = await repo_agent.execute(python_repo_state)

        # Step 2: Plan
        planner = PlannerAgent()
        state = await planner.execute(state)

        # Step 3: Generate
        generator = PipelineGeneratorAgent()
        state = await generator.execute(state)

        # Verify
        assert state.generated_pipeline is not None
        assert len(state.generated_pipeline.files) > 0

        primary = next(f for f in state.generated_pipeline.files if f.is_primary)
        assert primary.path == ".github/workflows/ci-cd.yml"

        # Validate the YAML is parseable
        config = yaml.safe_load(primary.content)
        assert "name" in config
        assert "on" in config
        assert "jobs" in config
        assert "ci" in config["jobs"]

    @pytest.mark.asyncio
    async def test_github_actions_has_checkout(self, python_repo_state: PipelineState):
        """Test that GitHub Actions workflow includes checkout step."""
        repo_agent = RepoAnalysisAgent()
        state = await repo_agent.execute(python_repo_state)

        planner = PlannerAgent()
        state = await planner.execute(state)

        generator = PipelineGeneratorAgent()
        state = await generator.execute(state)

        primary = next(f for f in state.generated_pipeline.files if f.is_primary)
        config = yaml.safe_load(primary.content)

        ci_steps = config["jobs"]["ci"]["steps"]
        assert any("checkout" in str(step.get("uses", "")) for step in ci_steps)

    @pytest.mark.asyncio
    async def test_docker_job_generated(self, python_repo_state: PipelineState):
        """Test that Docker build job is generated when Dockerfile exists."""
        repo_agent = RepoAnalysisAgent()
        state = await repo_agent.execute(python_repo_state)

        planner = PlannerAgent()
        state = await planner.execute(state)

        generator = PipelineGeneratorAgent()
        state = await generator.execute(state)

        primary = next(f for f in state.generated_pipeline.files if f.is_primary)
        config = yaml.safe_load(primary.content)

        assert "docker" in config["jobs"], "Docker job should be present when Dockerfile exists"
