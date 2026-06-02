"""Tests for the Repository Analysis Agent."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from src.agents.repo_analysis import RepoAnalysisAgent
from src.models import PipelineState


@pytest.fixture
def sample_python_repo() -> str:
    """Create a temporary Python repository for testing."""
    temp_dir = tempfile.mkdtemp(prefix="test_repo_")

    # Create Python project structure
    files = {
        "app.py": 'from fastapi import FastAPI\napp = FastAPI()\n',
        "requirements.txt": "fastapi==0.115.0\nuvicorn==0.30.0\npytest==8.0.0\n",
        "tests/test_app.py": "def test_example():\n    assert True\n",
        "Dockerfile": "FROM python:3.12-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"uvicorn\", \"app:app\"]\n",
        "docker-compose.yml": "version: '3.8'\nservices:\n  app:\n    build: .\n    ports:\n      - '8000:8000'\n",
        ".github/workflows/ci.yml": "name: CI\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n",
        "README.md": "# Test Project\n",
    }

    for filepath, content in files.items():
        full_path = Path(temp_dir) / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    yield temp_dir

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_node_repo() -> str:
    """Create a temporary Node.js repository for testing."""
    temp_dir = tempfile.mkdtemp(prefix="test_repo_node_")

    files = {
        "package.json": '{"name": "test-app", "scripts": {"test": "jest", "build": "tsc", "lint": "eslint ."}}',
        "src/index.ts": "console.log('hello');\n",
        "src/app.ts": "export const app = {};\n",
        "tsconfig.json": '{"compilerOptions": {"target": "ES2022"}}',
        "jest.config.ts": "export default { preset: 'ts-jest' };\n",
        "next.config.js": "module.exports = {};\n",
        "Dockerfile": "FROM node:20-alpine\nWORKDIR /app\nCOPY . .\nRUN npm ci\nCMD [\"npm\", \"start\"]\n",
    }

    for filepath, content in files.items():
        full_path = Path(temp_dir) / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    yield temp_dir

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestRepoAnalysisAgent:
    """Tests for RepoAnalysisAgent."""

    @pytest.mark.asyncio
    async def test_python_repo_analysis(self, sample_python_repo: str):
        """Test analysis of a Python repository."""
        agent = RepoAnalysisAgent()
        state = PipelineState(
            repo_url="https://github.com/test/test-repo",
            repo_local_path=sample_python_repo,
        )

        result = await agent.execute(state)
        analysis = result.repo_analysis

        assert analysis is not None
        assert any(l.name == "Python" for l in analysis.languages)
        assert "pip" in analysis.package_managers
        assert "FastAPI" in analysis.frameworks or "Flask" in analysis.frameworks
        assert "pytest" in analysis.test_frameworks
        assert analysis.containerization.has_dockerfile
        assert analysis.containerization.has_compose
        assert analysis.existing_ci.has_ci
        assert analysis.existing_ci.platform == "github_actions"

    @pytest.mark.asyncio
    async def test_node_repo_analysis(self, sample_node_repo: str):
        """Test analysis of a Node.js repository."""
        agent = RepoAnalysisAgent()
        state = PipelineState(
            repo_url="https://github.com/test/node-repo",
            repo_local_path=sample_node_repo,
        )

        result = await agent.execute(state)
        analysis = result.repo_analysis

        assert analysis is not None
        assert any(l.name == "TypeScript" for l in analysis.languages)
        assert "npm" in analysis.package_managers
        assert "Next.js" in analysis.frameworks
        assert "Jest" in analysis.test_frameworks
        assert analysis.containerization.has_dockerfile

    @pytest.mark.asyncio
    async def test_dockerfile_parsing(self, sample_python_repo: str):
        """Test Dockerfile parsing for base images."""
        agent = RepoAnalysisAgent()
        state = PipelineState(
            repo_url="https://github.com/test/test-repo",
            repo_local_path=sample_python_repo,
        )

        result = await agent.execute(state)
        container = result.repo_analysis.containerization

        assert container.has_dockerfile
        assert "python:3.12-slim" in container.base_images
        assert not container.multi_stage  # Single FROM

    @pytest.mark.asyncio
    async def test_empty_repo(self):
        """Test analysis of an empty repository."""
        temp_dir = tempfile.mkdtemp(prefix="test_empty_")
        try:
            agent = RepoAnalysisAgent()
            state = PipelineState(
                repo_url="https://github.com/test/empty-repo",
                repo_local_path=temp_dir,
            )

            result = await agent.execute(state)
            assert result.repo_analysis is not None
            assert len(result.repo_analysis.languages) == 0
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_file_tree_respects_ignore_dirs(self, sample_python_repo: str):
        """Test that ignored directories are excluded from file tree."""
        # Create a node_modules directory
        nm_dir = Path(sample_python_repo) / "node_modules" / "some-package"
        nm_dir.mkdir(parents=True)
        (nm_dir / "index.js").write_text("module.exports = {};")

        agent = RepoAnalysisAgent()
        file_tree = agent._get_file_tree(Path(sample_python_repo))

        assert not any("node_modules" in f for f in file_tree)
