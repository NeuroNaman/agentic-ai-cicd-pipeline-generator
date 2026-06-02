"""Pydantic models representing the core domain objects in the system."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ==============================================================================
# Repository Analysis Models
# ==============================================================================


class LanguageInfo(BaseModel):
    """Information about a detected programming language."""
    name: str
    version: Optional[str] = None
    percentage: float = Field(ge=0, le=100, description="Percentage of codebase")


class ContainerInfo(BaseModel):
    """Containerization details."""
    has_dockerfile: bool = False
    has_compose: bool = False
    dockerfile_path: Optional[str] = None
    compose_path: Optional[str] = None
    base_images: list[str] = Field(default_factory=list)
    multi_stage: bool = False


class InfraInfo(BaseModel):
    """Infrastructure-as-Code details."""
    has_terraform: bool = False
    has_pulumi: bool = False
    has_cloudformation: bool = False
    has_ansible: bool = False
    has_kubernetes: bool = False
    has_helm: bool = False
    terraform_providers: list[str] = Field(default_factory=list)
    cloud_provider: Optional[str] = None
    k8s_manifest_paths: list[str] = Field(default_factory=list)
    helm_chart_paths: list[str] = Field(default_factory=list)


class ExistingCIInfo(BaseModel):
    """Existing CI/CD configuration details."""
    has_ci: bool = False
    platform: Optional[str] = None
    config_path: Optional[str] = None
    config_content: Optional[str] = None
    is_valid: Optional[bool] = None
    issues: list[str] = Field(default_factory=list)


class EnvVar(BaseModel):
    """Environment variable specification."""
    name: str
    required: bool = True
    default: Optional[str] = None
    description: Optional[str] = None
    is_secret: bool = False


class ServiceInfo(BaseModel):
    """Service information for mono-repo sub-services."""
    name: str
    path: str
    language: str
    framework: Optional[str] = None
    has_dockerfile: bool = False
    entry_point: Optional[str] = None


class RepoAnalysis(BaseModel):
    """Complete repository analysis output."""
    repo_url: str
    repo_name: str
    default_branch: str = "main"
    languages: list[LanguageInfo] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    package_managers: list[str] = Field(default_factory=list)
    build_systems: list[str] = Field(default_factory=list)
    test_frameworks: list[str] = Field(default_factory=list)
    containerization: ContainerInfo = Field(default_factory=ContainerInfo)
    infrastructure: InfraInfo = Field(default_factory=InfraInfo)
    existing_ci: ExistingCIInfo = Field(default_factory=ExistingCIInfo)
    entry_points: list[str] = Field(default_factory=list)
    environment_variables: list[EnvVar] = Field(default_factory=list)
    secrets_required: list[str] = Field(default_factory=list)
    deployment_targets: list[str] = Field(default_factory=list)
    is_mono_repo: bool = False
    monorepo_tool: Optional[str] = None
    services: list[ServiceInfo] = Field(default_factory=list)
    raw_file_tree: list[str] = Field(default_factory=list)
    build_commands: dict[str, list[str]] = Field(default_factory=dict)
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==============================================================================
# Pipeline Planning Models
# ==============================================================================


class StageType(str, Enum):
    """Types of pipeline stages."""
    CHECKOUT = "checkout"
    SETUP = "setup"
    INSTALL = "install"
    LINT = "lint"
    TEST = "test"
    BUILD = "build"
    SECURITY_SCAN = "security_scan"
    DOCKER_BUILD = "docker_build"
    DOCKER_PUSH = "docker_push"
    DEPLOY = "deploy"
    SMOKE_TEST = "smoke_test"
    NOTIFY = "notify"
    CLEANUP = "cleanup"


class PipelineStage(BaseModel):
    """A single stage in the pipeline."""
    name: str
    stage_type: StageType
    commands: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    environment: dict[str, str] = Field(default_factory=dict)
    secrets: list[str] = Field(default_factory=list)
    timeout_minutes: int = 30
    continue_on_error: bool = False
    condition: Optional[str] = None
    runner: Optional[str] = None


class DeploymentStrategy(str, Enum):
    """Deployment strategies."""
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"


class Environment(BaseModel):
    """Deployment environment configuration."""
    name: str  # dev, staging, prod
    cloud_provider: Optional[str] = None
    region: Optional[str] = None
    config: dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False
    auto_deploy: bool = False


class ApprovalGate(BaseModel):
    """Approval gate between stages."""
    stage: str
    approvers: list[str] = Field(default_factory=list)
    auto_approve_after_minutes: Optional[int] = None
    required_approvals: int = 1


class RollbackConfig(BaseModel):
    """Rollback strategy configuration."""
    enabled: bool = True
    automatic: bool = False
    conditions: list[str] = Field(default_factory=lambda: ["deployment_failure", "health_check_failure"])
    max_rollback_attempts: int = 2


class SecretConfig(BaseModel):
    """Secret configuration for pipeline."""
    name: str
    source: str = "environment"  # environment | vault | aws_secrets_manager | github_secrets
    description: Optional[str] = None
    required: bool = True


class ResourceRequirements(BaseModel):
    """Resource requirements for pipeline execution."""
    cpu_cores: float = 2.0
    memory_gb: float = 4.0
    storage_gb: float = 10.0
    gpu: bool = False


class PipelinePlan(BaseModel):
    """Complete pipeline plan output from the Planner Agent."""
    target_platform: str  # github_actions | gitlab_ci | jenkins
    stages: list[PipelineStage] = Field(default_factory=list)
    deployment_strategy: DeploymentStrategy = DeploymentStrategy.ROLLING
    environments: list[Environment] = Field(default_factory=list)
    required_secrets: list[SecretConfig] = Field(default_factory=list)
    estimated_duration_minutes: int = 15
    resource_requirements: ResourceRequirements = Field(default_factory=ResourceRequirements)
    approval_gates: list[ApprovalGate] = Field(default_factory=list)
    rollback_strategy: RollbackConfig = Field(default_factory=RollbackConfig)
    triggers: list[str] = Field(default_factory=lambda: ["push to main", "pull request"])
    caching_strategy: dict[str, str] = Field(default_factory=dict)
    matrix_strategy: Optional[dict[str, list[str]]] = None


# ==============================================================================
# Pipeline Generation Models
# ==============================================================================


class GeneratedFile(BaseModel):
    """A file generated by the Pipeline Generation Agent."""
    path: str  # Relative path in the repo (e.g., .github/workflows/ci.yml)
    content: str
    description: str
    is_primary: bool = False  # True for the main CI/CD config file


class PipelineConfig(BaseModel):
    """Complete generated pipeline configuration."""
    files: list[GeneratedFile] = Field(default_factory=list)
    platform: str
    plan_hash: str = ""  # Hash of the plan used to generate this config
    generation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    notes: list[str] = Field(default_factory=list)  # Generation notes/decisions


# ==============================================================================
# Validation Models
# ==============================================================================


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationIssue(BaseModel):
    """A single validation issue."""
    severity: ValidationSeverity
    category: str  # syntax | semantic | security | performance
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


class ValidationReport(BaseModel):
    """Complete validation report."""
    passed: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    syntax_valid: bool = True
    semantic_valid: bool = True
    security_passed: bool = True
    dry_run_passed: Optional[bool] = None
    dry_run_logs: Optional[str] = None
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: float = 0.0


# ==============================================================================
# Execution Models
# ==============================================================================


class ExecutionStatus(str, Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ExecutionResult(BaseModel):
    """Result of pipeline execution."""
    run_id: str
    status: ExecutionStatus
    url: Optional[str] = None  # URL to the CI/CD run
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    logs: Optional[str] = None
    failed_stage: Optional[str] = None
    error_message: Optional[str] = None


# ==============================================================================
# Self-Healing Models
# ==============================================================================


class ErrorCategory(str, Enum):
    """Categories of pipeline errors."""
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"
    PERMISSION = "permission"
    INFRASTRUCTURE = "infrastructure"
    RESOURCE_LIMIT = "resource_limit"
    TEST_FAILURE = "test_failure"
    TIMEOUT = "timeout"
    NETWORK = "network"
    BUILD_FAILURE = "build_failure"
    DEPLOYMENT_FAILURE = "deployment_failure"
    UNKNOWN = "unknown"


class ErrorRecord(BaseModel):
    """Record of a pipeline error and its resolution."""
    error_message: str
    category: ErrorCategory
    root_cause: Optional[str] = None
    fix_applied: Optional[str] = None
    fix_successful: Optional[bool] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealingAction(BaseModel):
    """A self-healing action to fix a pipeline error."""
    description: str
    category: ErrorCategory
    changes: list[GeneratedFile] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1, description="Confidence in the fix")
    reasoning: str = ""


# ==============================================================================
# Orchestration State Model (LangGraph)
# ==============================================================================


class AgentIntent(str, Enum):
    """User intent classification."""
    GENERATE = "generate"
    VALIDATE = "validate"
    FIX = "fix"
    DEPLOY = "deploy"
    MONITOR = "monitor"
    EXPLAIN = "explain"


class PipelineState(BaseModel):
    """
    Central state object passed through the LangGraph agent pipeline.
    This is the single source of truth for the entire orchestration flow.
    """

    # --- User Request ---
    user_request: str = ""
    intent: AgentIntent = AgentIntent.GENERATE

    # --- Repository Context ---
    repo_url: str = ""
    repo_local_path: Optional[str] = None
    repo_analysis: Optional[RepoAnalysis] = None

    # --- Pipeline Artifacts ---
    pipeline_plan: Optional[PipelinePlan] = None
    generated_pipeline: Optional[PipelineConfig] = None
    validation_report: Optional[ValidationReport] = None
    execution_result: Optional[ExecutionResult] = None

    # --- Execution State ---
    current_stage: str = "intake"  # intake | analyzing | planning | generating | validating | deploying | healing
    execution_logs: list[str] = Field(default_factory=list)
    error_history: list[ErrorRecord] = Field(default_factory=list)

    # --- Control Flow ---
    retry_count: int = 0
    max_retries: int = 3
    requires_approval: bool = True
    approved: bool = False

    # --- RAG Context ---
    similar_pipelines: list[dict[str, Any]] = Field(default_factory=list)

    # --- Messages ---
    messages: list[dict[str, str]] = Field(default_factory=list)  # Conversation history

    # --- Metadata ---
    session_id: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
