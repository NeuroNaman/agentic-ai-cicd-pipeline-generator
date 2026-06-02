"""
FastAPI server — REST API for the Agentic CI/CD Engineer.

Provides endpoints for:
- Pipeline generation
- Pipeline validation
- Pipeline status
- Health checks
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import structlog
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from src.config import get_settings

logger = structlog.get_logger()

# ==============================================================================
# Request/Response Models
# ==============================================================================


class GenerateRequest(BaseModel):
    """Request to generate a CI/CD pipeline."""
    repo_url: str = Field(..., description="Repository URL")
    platform: str = Field(default="github_actions", description="Target CI/CD platform")
    auto_approve: bool = Field(default=False, description="Skip human approval")
    constraints: dict[str, Any] = Field(default_factory=dict, description="Custom constraints")


class GenerateResponse(BaseModel):
    """Response with generated pipeline."""
    session_id: str
    status: str  # "pending" | "running" | "completed" | "failed"
    message: str


class PipelineStatusResponse(BaseModel):
    """Pipeline generation status."""
    session_id: str
    status: str
    current_stage: str
    execution_logs: list[str]
    generated_files: list[dict[str, str]] | None = None
    validation_passed: bool | None = None
    error_message: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    timestamp: str


# ==============================================================================
# In-memory session store (replace with Redis/DB in production)
# ==============================================================================

_sessions: dict[str, dict[str, Any]] = {}


# ==============================================================================
# App Factory
# ==============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    logger.info("api_starting", host=get_settings().api_host, port=get_settings().api_port)
    yield
    logger.info("api_shutting_down")


def create_api() -> FastAPI:
    """Create the FastAPI application."""
    settings = get_settings()

    api = FastAPI(
        title="Agentic CI/CD Engineer API",
        description="AI-powered CI/CD pipeline generation and management",
        version="0.1.0",
        lifespan=lifespan,
    )

    # ---- Health ----
    @api.get("/health", response_model=HealthResponse)
    async def health():
        from src import __version__
        return HealthResponse(
            version=__version__,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    # ---- Generate Pipeline ----
    @api.post("/api/v1/generate", response_model=GenerateResponse)
    async def generate_pipeline(request: GenerateRequest, background_tasks: BackgroundTasks):
        session_id = str(uuid4())[:8]

        _sessions[session_id] = {
            "status": "pending",
            "request": request.model_dump(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Run generation in background
        background_tasks.add_task(_run_pipeline_generation, session_id, request)

        return GenerateResponse(
            session_id=session_id,
            status="pending",
            message="Pipeline generation started. Use /api/v1/status/{session_id} to check progress.",
        )

    # ---- Pipeline Status ----
    @api.get("/api/v1/status/{session_id}", response_model=PipelineStatusResponse)
    async def get_status(session_id: str):
        if session_id not in _sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = _sessions[session_id]
        state = session.get("state", {})

        return PipelineStatusResponse(
            session_id=session_id,
            status=session.get("status", "unknown"),
            current_stage=state.get("current_stage", "unknown"),
            execution_logs=state.get("execution_logs", []),
            generated_files=[
                {"path": f["path"], "content": f["content"]}
                for f in state.get("generated_pipeline", {}).get("files", [])
            ] if state.get("generated_pipeline") else None,
            validation_passed=state.get("validation_report", {}).get("passed")
            if state.get("validation_report") else None,
        )

    # ---- Approve Pipeline ----
    @api.post("/api/v1/approve/{session_id}")
    async def approve_pipeline(session_id: str):
        if session_id not in _sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        _sessions[session_id]["state"]["approved"] = True
        return {"message": "Pipeline approved"}

    # ---- List Sessions ----
    @api.get("/api/v1/sessions")
    async def list_sessions():
        result = []
        for sid, data in _sessions.items():
            state = data.get("state") or {}
            repo_analysis = state.get("repo_analysis") or {}
            gen_pipeline = state.get("generated_pipeline") or {}
            val_report = state.get("validation_report") or {}

            # frameworks / languages may be strings or dicts depending on serialization
            raw_frameworks = repo_analysis.get("frameworks", []) or []
            raw_languages = repo_analysis.get("languages", []) or []

            def extract_name(item):
                if isinstance(item, dict):
                    return item.get("name", str(item))
                return str(item)

            # generated_files: list of dicts with {path, content} or plain strings
            raw_files = gen_pipeline.get("files", []) or []
            def extract_path(f):
                if isinstance(f, dict):
                    return f.get("path", "")
                return str(f)

            result.append({
                "session_id": sid,
                "status": data.get("status"),
                "created_at": data.get("created_at"),
                "repo_url": data.get("request", {}).get("repo_url", ""),
                "platform": data.get("request", {}).get("platform", "github_actions"),
                "validation_passed": val_report.get("passed") if val_report else None,
                "generated_files": [extract_path(f) for f in raw_files],
                "frameworks": [extract_name(f) for f in raw_frameworks],
                "languages": [extract_name(lang) for lang in raw_languages],
            })
        return result

    return api


async def _run_pipeline_generation(session_id: str, request: GenerateRequest) -> None:
    """Background task to run pipeline generation."""
    from src.agents.orchestrator import create_app
    from src.models import PipelineState

    _sessions[session_id]["status"] = "running"

    try:
        initial_state = PipelineState(
            user_request=f"Generate a {request.platform} CI/CD pipeline for {request.repo_url}",
            repo_url=request.repo_url,
            requires_approval=not request.auto_approve,
            approved=request.auto_approve,
            session_id=session_id,
            started_at=datetime.now(timezone.utc),
        ).model_dump()

        graph_app = create_app()
        result = await graph_app.ainvoke(initial_state)

        _sessions[session_id]["state"] = result
        _sessions[session_id]["status"] = result.get("current_stage", "completed")

    except Exception as e:
        logger.error("generation_failed", session_id=session_id, error=str(e))
        _sessions[session_id]["status"] = "failed"
        _sessions[session_id]["error"] = str(e)
