"""
Supervisor / Orchestrator — LangGraph state machine that coordinates all agents.

This is the central orchestration layer that:
- Parses user requests
- Routes tasks to specialized agents
- Manages state and checkpointing
- Handles conditional branching (validation pass/fail, retries)
- Supports human-in-the-loop approval
"""

from __future__ import annotations

from typing import Any

import structlog
from langgraph.graph import END, StateGraph

from src.agents.pipeline_generator import PipelineGeneratorAgent
from src.agents.planner import PlannerAgent
from src.agents.repo_analysis import RepoAnalysisAgent
from src.agents.self_healing import SelfHealingAgent
from src.agents.validation import ValidationAgent
from src.models import PipelineState

logger = structlog.get_logger()


# ==============================================================================
# Routing Functions (Conditional Edges)
# ==============================================================================


def route_after_validation(state: dict[str, Any]) -> str:
    """
    Route after validation based on results.

    Returns:
        "approved" — if validation passed and auto-approve is on
        "needs_approval" — if validation passed but needs human approval
        "healing" — if validation failed and retries remain
        "failed" — if max retries exceeded
    """
    pipeline_state = PipelineState(**state)
    report = pipeline_state.validation_report

    if report and report.passed:
        if pipeline_state.requires_approval and not pipeline_state.approved:
            return "needs_approval"
        return "approved"

    # Validation failed — check retry budget
    if pipeline_state.retry_count < pipeline_state.max_retries:
        return "healing"

    return "failed"


def route_after_execution(state: dict[str, Any]) -> str:
    """Route after pipeline execution."""
    pipeline_state = PipelineState(**state)

    if pipeline_state.execution_result and pipeline_state.execution_result.status.value == "success":
        return "success"

    if pipeline_state.retry_count < pipeline_state.max_retries:
        return "healing"

    return "failed"


def route_after_approval(state: dict[str, Any]) -> str:
    """Route after human approval."""
    pipeline_state = PipelineState(**state)

    if pipeline_state.approved:
        return "execute"

    return "regenerate"


# ==============================================================================
# Human-in-the-Loop Node
# ==============================================================================


async def human_approval_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Placeholder for human-in-the-loop approval.

    In the actual system, this would:
    1. Send the generated pipeline to the user for review
    2. Wait for approval/rejection
    3. Update state based on response

    With LangGraph's interrupt mechanism, this becomes a checkpoint
    where execution pauses until the human responds.
    """
    pipeline_state = PipelineState(**state)

    # Log what's awaiting approval
    logger.info(
        "awaiting_approval",
        pipeline_files=[f.path for f in pipeline_state.generated_pipeline.files]
        if pipeline_state.generated_pipeline
        else [],
        validation_passed=pipeline_state.validation_report.passed
        if pipeline_state.validation_report
        else None,
    )

    # In auto-approve mode (for testing), approve automatically
    if not pipeline_state.requires_approval:
        pipeline_state.approved = True

    return pipeline_state.model_dump()


# ==============================================================================
# Terminal Nodes
# ==============================================================================


async def success_node(state: dict[str, Any]) -> dict[str, Any]:
    """Terminal success node."""
    pipeline_state = PipelineState(**state)
    pipeline_state.current_stage = "completed"
    pipeline_state.execution_logs.append("[Supervisor] Pipeline completed successfully!")
    logger.info("pipeline_completed", session_id=pipeline_state.session_id)
    return pipeline_state.model_dump()


async def failure_node(state: dict[str, Any]) -> dict[str, Any]:
    """Terminal failure node — max retries exceeded."""
    pipeline_state = PipelineState(**state)
    pipeline_state.current_stage = "failed"
    pipeline_state.execution_logs.append(
        f"[Supervisor] Pipeline failed after {pipeline_state.retry_count} retries. "
        "Manual intervention required."
    )
    logger.error(
        "pipeline_failed",
        retry_count=pipeline_state.retry_count,
        error_history=[e.error_message[:100] for e in pipeline_state.error_history],
    )
    return pipeline_state.model_dump()


# ==============================================================================
# Build the LangGraph Workflow
# ==============================================================================


def build_workflow() -> StateGraph:
    """
    Build the complete LangGraph workflow for the Agentic CI/CD Engineer.

    Graph structure:
        repo_analysis → planner → generator → validator
            ├── [passed] → approval → executor → success
            ├── [failed] → healer → generator (loop)
            └── [max_retries] → failure
    """
    # Instantiate agents
    repo_analysis_agent = RepoAnalysisAgent()
    planner_agent = PlannerAgent()
    generator_agent = PipelineGeneratorAgent()
    validation_agent = ValidationAgent()
    healing_agent = SelfHealingAgent()

    # Build graph
    workflow = StateGraph(dict)  # Using dict for LangGraph compatibility

    # Add nodes
    workflow.add_node("repo_analysis", repo_analysis_agent)
    workflow.add_node("planner", planner_agent)
    workflow.add_node("generator", generator_agent)
    workflow.add_node("validator", validation_agent)
    workflow.add_node("healer", healing_agent)
    workflow.add_node("approval", human_approval_node)
    workflow.add_node("success", success_node)
    workflow.add_node("failure", failure_node)

    # Define edges
    workflow.set_entry_point("repo_analysis")

    # Linear flow: analysis → planning → generation → validation
    workflow.add_edge("repo_analysis", "planner")
    workflow.add_edge("planner", "generator")
    workflow.add_edge("generator", "validator")

    # Conditional: after validation
    workflow.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "approved": "success",          # Auto-approved
            "needs_approval": "approval",   # Needs human review
            "healing": "healer",            # Validation failed, try to fix
            "failed": "failure",            # Max retries exceeded
        },
    )

    # Conditional: after human approval
    workflow.add_conditional_edges(
        "approval",
        route_after_approval,
        {
            "execute": "success",       # Approved → proceed
            "regenerate": "generator",  # Rejected → regenerate
        },
    )

    # Self-healing loops back to generator
    workflow.add_edge("healer", "generator")

    # Terminal nodes
    workflow.add_edge("success", END)
    workflow.add_edge("failure", END)

    return workflow


def create_app():
    """Create the compiled LangGraph application."""
    workflow = build_workflow()
    return workflow.compile()
