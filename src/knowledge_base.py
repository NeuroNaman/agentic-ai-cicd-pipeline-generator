"""
Knowledge Base — RAG pipeline for retrieving similar CI/CD configurations.

Embeds pipeline templates and past successful configs into a vector store,
enabling retrieval of relevant examples during pipeline generation.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


class PipelineKnowledgeBase:
    """
    Vector-backed knowledge base for CI/CD pipeline templates.

    Stores embedded pipeline configurations with metadata for similarity search.
    Used by the Pipeline Generator Agent to retrieve relevant examples.
    """

    def __init__(self, persist_dir: str = "./data/chromadb") -> None:
        self.persist_dir = persist_dir
        self._collection = None

    def _get_collection(self):
        """Lazy-load ChromaDB collection."""
        if self._collection is None:
            import chromadb

            client = chromadb.PersistentClient(path=self.persist_dir)
            self._collection = client.get_or_create_collection(
                name="pipeline_templates",
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def add_template(
        self,
        template_id: str,
        content: str,
        metadata: dict[str, Any],
    ) -> None:
        """
        Add a pipeline template to the knowledge base.

        Args:
            template_id: Unique identifier for the template.
            content: Pipeline configuration content (YAML/JSON).
            metadata: Template metadata (language, framework, platform, etc.).
        """
        collection = self._get_collection()
        collection.add(
            ids=[template_id],
            documents=[content],
            metadatas=[metadata],
        )
        logger.info("template_added", template_id=template_id)

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for similar pipeline templates.

        Args:
            query: Natural language description of desired pipeline.
            n_results: Number of results to return.
            filter_metadata: Optional metadata filters.

        Returns:
            List of matching templates with content and metadata.
        """
        collection = self._get_collection()

        kwargs: dict[str, Any] = {
            "query_texts": [query],
            "n_results": n_results,
        }
        if filter_metadata:
            kwargs["where"] = filter_metadata

        results = collection.query(**kwargs)

        templates = []
        for i in range(len(results["ids"][0])):
            templates.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else None,
            })

        return templates

    def load_templates_from_directory(self, templates_dir: str) -> int:
        """
        Bulk-load pipeline templates from a directory.

        Expects files with .yml/.yaml extension and optional .meta.json sidecar files.

        Returns:
            Number of templates loaded.
        """
        import json

        count = 0
        templates_path = Path(templates_dir)

        if not templates_path.exists():
            logger.warning("templates_dir_not_found", path=templates_dir)
            return 0

        for template_file in templates_path.glob("**/*.yml"):
            content = template_file.read_text()
            template_id = template_file.stem

            # Look for metadata sidecar
            meta_file = template_file.with_suffix(".meta.json")
            metadata: dict[str, Any] = {"source": "templates_dir"}
            if meta_file.exists():
                metadata.update(json.loads(meta_file.read_text()))

            self.add_template(template_id, content, metadata)
            count += 1

        logger.info("templates_loaded", count=count, source=templates_dir)
        return count

    def record_successful_run(
        self,
        pipeline_config: str,
        repo_analysis_summary: str,
        platform: str,
        languages: list[str],
        frameworks: list[str],
    ) -> None:
        """
        Record a successfully validated pipeline for future retrieval.

        This is how the system learns from past runs.
        """
        import hashlib

        config_hash = hashlib.sha256(pipeline_config.encode()).hexdigest()[:12]
        template_id = f"run_{config_hash}"

        self.add_template(
            template_id=template_id,
            content=pipeline_config,
            metadata={
                "source": "successful_run",
                "platform": platform,
                "languages": ",".join(languages),
                "frameworks": ",".join(frameworks),
                "repo_summary": repo_analysis_summary[:500],
            },
        )

    def get_stats(self) -> dict[str, Any]:
        """Get knowledge base statistics."""
        collection = self._get_collection()
        return {
            "total_templates": collection.count(),
            "persist_dir": self.persist_dir,
        }
