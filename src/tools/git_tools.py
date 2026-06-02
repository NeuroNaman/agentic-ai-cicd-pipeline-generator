"""
Git tools — Repository cloning, reading, and manipulation.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import structlog

logger = structlog.get_logger()


async def clone_repository(repo_url: str, branch: str = "main", depth: int = 1) -> str:
    """
    Clone a Git repository to a temporary directory.

    Args:
        repo_url: The URL of the repository to clone.
        branch: The branch to clone.
        depth: Clone depth (1 for shallow clone).

    Returns:
        Path to the cloned repository.
    """
    from git import Repo

    temp_dir = tempfile.mkdtemp(prefix="cicd_agent_repo_")
    logger.info("cloning_repository", url=repo_url, branch=branch, dest=temp_dir)

    try:
        Repo.clone_from(
            repo_url,
            temp_dir,
            branch=branch,
            depth=depth,
            single_branch=True,
        )
        logger.info("clone_complete", path=temp_dir)
        return temp_dir
    except Exception as e:
        # Cleanup on failure
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.error("clone_failed", error=str(e))
        raise


async def read_file(repo_path: str, file_path: str) -> str:
    """
    Read a file from the repository.

    Args:
        repo_path: Path to the cloned repository.
        file_path: Relative path to the file within the repository.

    Returns:
        File contents as string.
    """
    full_path = Path(repo_path) / file_path

    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not full_path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    return full_path.read_text(encoding="utf-8", errors="replace")


async def list_directory(repo_path: str, dir_path: str = ".") -> list[str]:
    """
    List contents of a directory in the repository.

    Args:
        repo_path: Path to the cloned repository.
        dir_path: Relative path to the directory.

    Returns:
        List of file/directory names.
    """
    full_path = Path(repo_path) / dir_path

    if not full_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    entries = []
    for entry in sorted(full_path.iterdir()):
        name = entry.name
        if entry.is_dir():
            name += "/"
        entries.append(name)

    return entries


async def get_file_tree(
    repo_path: str,
    max_depth: int = 5,
    ignore_dirs: set[str] | None = None,
) -> list[str]:
    """
    Get the complete file tree of a repository.

    Args:
        repo_path: Path to the cloned repository.
        max_depth: Maximum directory depth to traverse.
        ignore_dirs: Set of directory names to skip.

    Returns:
        List of relative file paths.
    """
    if ignore_dirs is None:
        ignore_dirs = {
            ".git", "node_modules", "__pycache__", ".venv", "venv",
            ".tox", "dist", "build", ".next", ".nuxt", "target",
            ".gradle", ".idea", ".vscode",
        }

    files: list[str] = []
    root = Path(repo_path)

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored directories
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

        rel_dir = Path(dirpath).relative_to(root)
        depth = len(rel_dir.parts)
        if depth > max_depth:
            continue

        for filename in filenames:
            rel_path = str(rel_dir / filename) if str(rel_dir) != "." else filename
            files.append(rel_path)

    return sorted(files)


def cleanup_repo(repo_path: str) -> None:
    """Remove a cloned repository directory."""
    shutil.rmtree(repo_path, ignore_errors=True)
    logger.info("repo_cleaned_up", path=repo_path)
