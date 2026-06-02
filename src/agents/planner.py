# """
# Planner Agent — Strategic pipeline planning based on repository analysis.

# Takes the RepoAnalysis and determines:
# - Which CI/CD platform to target
# - What stages the pipeline needs
# - Deployment strategy
# - Environment configuration
# - Approval gates
# """

# from __future__ import annotations

# from typing import Any

# import structlog

# from src.agents.base import BaseAgent
# from src.models import (
#     ApprovalGate,
#     DeploymentStrategy,
#     Environment,
#     PipelinePlan,
#     PipelineStage,
#     PipelineState,
#     RollbackConfig,
#     SecretConfig,
#     StageType,
# )

# logger = structlog.get_logger()

# # Default stage templates per language/framework
# STAGE_TEMPLATES: dict[str, list[dict[str, Any]]] = {
#     "python": [
#         {"name": "Install Dependencies", "type": StageType.INSTALL, "commands": ["pip install -r requirements.txt"]},
#         {"name": "Lint", "type": StageType.LINT, "commands": ["ruff check .", "mypy ."]},
#         {"name": "Test", "type": StageType.TEST, "commands": ["pytest --cov"]},
#     ],
#     "javascript": [
#         {"name": "Install Dependencies", "type": StageType.INSTALL, "commands": ["npm ci"]},
#         {"name": "Lint", "type": StageType.LINT, "commands": ["npm run lint"]},
#         {"name": "Test", "type": StageType.TEST, "commands": ["npm test"]},
#         {"name": "Build", "type": StageType.BUILD, "commands": ["npm run build"]},
#     ],
#     "go": [
#         {"name": "Install Dependencies", "type": StageType.INSTALL, "commands": ["go mod download"]},
#         {"name": "Lint", "type": StageType.LINT, "commands": ["golangci-lint run"]},
#         {"name": "Test", "type": StageType.TEST, "commands": ["go test ./..."]},
#         {"name": "Build", "type": StageType.BUILD, "commands": ["go build -o app ./cmd/..."]},
#     ],
#     "java": [
#         {"name": "Build & Test", "type": StageType.BUILD, "commands": ["mvn clean verify"]},
#     ],
#     "rust": [
#         {"name": "Build", "type": StageType.BUILD, "commands": ["cargo build --release"]},
#         {"name": "Test", "type": StageType.TEST, "commands": ["cargo test"]},
#         {"name": "Lint", "type": StageType.LINT, "commands": ["cargo clippy -- -D warnings"]},
#     ],
# }


# class PlannerAgent(BaseAgent):
#     """
#     Creates a strategic pipeline plan based on repository analysis.

#     Uses heuristics + LLM to determine the optimal pipeline configuration.
#     """

#     def __init__(self) -> None:
#         super().__init__(
#             name="PlannerAgent",
#             description="Creates strategic CI/CD pipeline plans from repository analysis",
#         )

#     async def execute(self, state: PipelineState) -> PipelineState:
#         """Create a pipeline plan based on repo analysis."""
#         state.current_stage = "planning"

#         if not state.repo_analysis:
#             raise ValueError("RepoAnalysis is required before planning. Run RepoAnalysisAgent first.")

#         analysis = state.repo_analysis

#         # Determine target platform
#         platform = self._determine_platform(analysis)

#         # Build pipeline stages
#         stages = self._build_stages(analysis)

#         # Determine deployment strategy
#         deployment_strategy = self._determine_deployment_strategy(analysis)

#         # Configure environments
#         environments = self._configure_environments(analysis)

#         # Identify required secrets
#         secrets = self._identify_secrets(analysis)

#         # Set up approval gates
#         approval_gates = self._configure_approval_gates(state)

#         # Build the plan
#         state.pipeline_plan = PipelinePlan(
#             target_platform=platform,
#             stages=stages,
#             deployment_strategy=deployment_strategy,
#             environments=environments,
#             required_secrets=secrets,
#             estimated_duration_minutes=self._estimate_duration(stages),
#             approval_gates=approval_gates,
#             rollback_strategy=RollbackConfig(
#                 enabled=True,
#                 automatic=deployment_strategy != DeploymentStrategy.CANARY,
#             ),
#             triggers=["push to main", "pull_request"],
#             caching_strategy=self._determine_caching(analysis),
#         )

#         self._log(
#             "plan_created",
#             platform=platform,
#             num_stages=len(stages),
#             deployment_strategy=deployment_strategy.value,
#         )

#         return state

#     def _determine_platform(self, analysis: Any) -> str:
#         """Determine the best CI/CD platform."""
#         # If existing CI exists, use the same platform
#         if analysis.existing_ci.has_ci and analysis.existing_ci.platform:
#             return analysis.existing_ci.platform

#         # GitHub repos → GitHub Actions
#         if "github.com" in analysis.repo_url:
#             return "github_actions"

#         # GitLab repos → GitLab CI
#         if "gitlab" in analysis.repo_url:
#             return "gitlab_ci"

#         # Default to GitHub Actions
#         return "github_actions"

#     def _build_stages(self, analysis: Any) -> list[PipelineStage]:
#         """Build pipeline stages based on detected tech stack."""
#         stages: list[PipelineStage] = []

#         # Checkout stage (always first)
#         stages.append(PipelineStage(
#             name="Checkout",
#             stage_type=StageType.CHECKOUT,
#             commands=["checkout repository"],
#         ))

#         # Setup stage — runtime setup
#         primary_lang = analysis.languages[0].name.lower() if analysis.languages else "python"
#         stages.append(PipelineStage(
#             name=f"Setup {primary_lang.title()}",
#             stage_type=StageType.SETUP,
#             commands=[f"setup {primary_lang} runtime"],
#         ))

#         # Language-specific stages
#         if primary_lang in STAGE_TEMPLATES:
#             for template in STAGE_TEMPLATES[primary_lang]:
#                 stages.append(PipelineStage(
#                     name=template["name"],
#                     stage_type=template["type"],
#                     commands=template["commands"],
#                 ))

#         # Docker build stage (if Dockerfile exists)
#         if analysis.containerization.has_dockerfile:
#             stages.append(PipelineStage(
#                 name="Docker Build",
#                 stage_type=StageType.DOCKER_BUILD,
#                 commands=["docker build -t $IMAGE_NAME ."],
#             ))
#             stages.append(PipelineStage(
#                 name="Docker Push",
#                 stage_type=StageType.DOCKER_PUSH,
#                 commands=["docker push $IMAGE_NAME"],
#                 depends_on=["Docker Build"],
#             ))

#         # Deployment stage
#         if analysis.infrastructure.has_kubernetes:
#             stages.append(PipelineStage(
#                 name="Deploy to Kubernetes",
#                 stage_type=StageType.DEPLOY,
#                 commands=["kubectl apply -f k8s/"],
#                 depends_on=["Docker Push"] if analysis.containerization.has_dockerfile else [],
#             ))
#         elif analysis.infrastructure.has_terraform:
#             stages.append(PipelineStage(
#                 name="Terraform Apply",
#                 stage_type=StageType.DEPLOY,
#                 commands=["terraform init", "terraform plan", "terraform apply -auto-approve"],
#             ))

#         return stages

#     def _determine_deployment_strategy(self, analysis: Any) -> DeploymentStrategy:
#         """Determine the deployment strategy."""
#         if analysis.infrastructure.has_kubernetes:
#             return DeploymentStrategy.ROLLING
#         return DeploymentStrategy.RECREATE

#     def _configure_environments(self, analysis: Any) -> list[Environment]:
#         """Configure deployment environments."""
#         environments = [
#             Environment(name="development", auto_deploy=True),
#             Environment(name="staging", auto_deploy=True, requires_approval=False),
#             Environment(name="production", requires_approval=True, auto_deploy=False),
#         ]

#         # Set cloud provider if detected
#         if analysis.infrastructure.cloud_provider:
#             for env in environments:
#                 env.cloud_provider = analysis.infrastructure.cloud_provider

#         return environments

#     def _identify_secrets(self, analysis: Any) -> list[SecretConfig]:
#         """Identify required secrets for the pipeline."""
#         secrets: list[SecretConfig] = []

#         if analysis.containerization.has_dockerfile:
#             secrets.extend([
#                 SecretConfig(name="DOCKER_USERNAME", description="Docker registry username"),
#                 SecretConfig(name="DOCKER_PASSWORD", description="Docker registry password"),
#             ])

#         if analysis.infrastructure.has_terraform:
#             secrets.extend([
#                 SecretConfig(name="AWS_ACCESS_KEY_ID", description="AWS access key"),
#                 SecretConfig(name="AWS_SECRET_ACCESS_KEY", description="AWS secret key"),
#             ])

#         if analysis.infrastructure.has_kubernetes:
#             secrets.append(
#                 SecretConfig(name="KUBECONFIG", description="Kubernetes config")
#             )

#         return secrets

#     def _configure_approval_gates(self, state: PipelineState) -> list[ApprovalGate]:
#         """Configure approval gates."""
#         if not state.requires_approval:
#             return []

#         return [
#             ApprovalGate(
#                 stage="Deploy to Production",
#                 required_approvals=1,
#                 auto_approve_after_minutes=60,
#             )
#         ]

#     def _estimate_duration(self, stages: list[PipelineStage]) -> int:
#         """Estimate pipeline duration in minutes."""
#         # Rough estimate: 2 min per stage + extra for build/deploy
#         base = len(stages) * 2
#         for stage in stages:
#             if stage.stage_type in (StageType.BUILD, StageType.DOCKER_BUILD):
#                 base += 5
#             elif stage.stage_type == StageType.DEPLOY:
#                 base += 3
#             elif stage.stage_type == StageType.TEST:
#                 base += 3
#         return base

#     def _determine_caching(self, analysis: Any) -> dict[str, str]:
#         """Determine caching strategy."""
#         cache = {}

#         for manager in analysis.package_managers:
#             if manager in ("npm", "yarn", "pnpm"):
#                 cache["node_modules"] = "~/.npm"
#             elif manager in ("pip", "poetry/pip", "pipenv"):
#                 cache["pip"] = "~/.cache/pip"
#             elif manager == "go modules":
#                 cache["go"] = "~/go/pkg/mod"
#             elif manager in ("maven", "gradle"):
#                 cache["java"] = "~/.m2/repository"
#             elif manager == "cargo":
#                 cache["cargo"] = "~/.cargo"

#         return cache



"""
Planner Agent — Strategic pipeline planning based on repository analysis.

Takes the RepoAnalysis and determines:
- Which CI/CD platform to target
- What stages the pipeline needs
- Deployment strategy
- Environment configuration
- Approval gates
"""

from __future__ import annotations

from typing import Any

import structlog

from src.agents.base import BaseAgent
from src.models import (
    ApprovalGate,
    DeploymentStrategy,
    Environment,
    PipelinePlan,
    PipelineStage,
    PipelineState,
    RollbackConfig,
    SecretConfig,
    StageType,
)

logger = structlog.get_logger()

# Default stage templates per language/framework
STAGE_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "python": [
        {"name": "Install Dependencies", "type": StageType.INSTALL, "commands": ["pip install -r requirements.txt"]},
        {"name": "Lint", "type": StageType.LINT, "commands": ["ruff check .", "mypy ."]},
        {"name": "Test", "type": StageType.TEST, "commands": ["pytest --cov"]},
    ],
    "javascript": [
        {"name": "Install Dependencies", "type": StageType.INSTALL, "commands": ["npm ci"]},
        {"name": "Lint", "type": StageType.LINT, "commands": ["npm run lint"]},
        {"name": "Test", "type": StageType.TEST, "commands": ["npm test"]},
        {"name": "Build", "type": StageType.BUILD, "commands": ["npm run build"]},
    ],
    "typescript": [
        {"name": "Install Dependencies", "type": StageType.INSTALL, "commands": ["npm ci"]},
        {"name": "Lint", "type": StageType.LINT, "commands": ["npm run lint"]},
        {"name": "Test", "type": StageType.TEST, "commands": ["npm test"]},
        {"name": "Build", "type": StageType.BUILD, "commands": ["npm run build"]},
    ],
    "nodejs": [
        {"name": "Install Dependencies", "type": StageType.INSTALL, "commands": ["npm ci"]},
        {"name": "Lint", "type": StageType.LINT, "commands": ["npm run lint"]},
        {"name": "Test", "type": StageType.TEST, "commands": ["npm test"]},
        {"name": "Build", "type": StageType.BUILD, "commands": ["npm run build"]},
    ],
    "go": [
        {"name": "Install Dependencies", "type": StageType.INSTALL, "commands": ["go mod download"]},
        {"name": "Lint", "type": StageType.LINT, "commands": ["golangci-lint run"]},
        {"name": "Test", "type": StageType.TEST, "commands": ["go test ./..."]},
        {"name": "Build", "type": StageType.BUILD, "commands": ["go build -o app ./cmd/..."]},
    ],
    "java": [
        {"name": "Build & Test", "type": StageType.BUILD, "commands": ["mvn clean verify"]},
    ],
    "rust": [
        {"name": "Build", "type": StageType.BUILD, "commands": ["cargo build --release"]},
        {"name": "Test", "type": StageType.TEST, "commands": ["cargo test"]},
        {"name": "Lint", "type": StageType.LINT, "commands": ["cargo clippy -- -D warnings"]},
    ],
    "ruby": [
        {"name": "Install Dependencies", "type": StageType.INSTALL, "commands": ["bundle install"]},
        {"name": "Test", "type": StageType.TEST, "commands": ["bundle exec rspec"]},
    ],
    "php": [
        {"name": "Install Dependencies", "type": StageType.INSTALL, "commands": ["composer install"]},
        {"name": "Test", "type": StageType.TEST, "commands": ["php artisan test"]},
    ],
}


class PlannerAgent(BaseAgent):
    """
    Creates a strategic pipeline plan based on repository analysis.

    Uses heuristics + LLM to determine the optimal pipeline configuration.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PlannerAgent",
            description="Creates strategic CI/CD pipeline plans from repository analysis",
        )

    async def execute(self, state: PipelineState) -> PipelineState:
        """Create a pipeline plan based on repo analysis."""
        state.current_stage = "planning"

        if not state.repo_analysis:
            raise ValueError("RepoAnalysis is required before planning. Run RepoAnalysisAgent first.")

        analysis = state.repo_analysis

        # Determine target platform — now passes state so user --platform flag is respected
        platform = self._determine_platform(analysis, state)

        # Build pipeline stages
        stages = self._build_stages(analysis)

        # Determine deployment strategy
        deployment_strategy = self._determine_deployment_strategy(analysis)

        # Configure environments
        environments = self._configure_environments(analysis)

        # Identify required secrets
        secrets = self._identify_secrets(analysis)

        # Set up approval gates
        approval_gates = self._configure_approval_gates(state)

        # Build the plan
        state.pipeline_plan = PipelinePlan(
            target_platform=platform,
            stages=stages,
            deployment_strategy=deployment_strategy,
            environments=environments,
            required_secrets=secrets,
            estimated_duration_minutes=self._estimate_duration(stages),
            approval_gates=approval_gates,
            rollback_strategy=RollbackConfig(
                enabled=True,
                automatic=deployment_strategy != DeploymentStrategy.CANARY,
            ),
            triggers=["push to main", "pull_request"],
            caching_strategy=self._determine_caching(analysis),
        )

        self._log(
            "plan_created",
            platform=platform,
            num_stages=len(stages),
            deployment_strategy=deployment_strategy.value,
        )

        return state

    def _determine_platform(self, analysis: Any, state: Any) -> str:
        """
        Determine the best CI/CD platform.

        Priority order:
        1. User explicitly passed --platform flag (read from user_request)
        2. Existing CI/CD config found in repo
        3. Auto-detect from repo URL
        4. Default to github_actions
        """

        # Priority 1 — respect user's --platform flag
        # The CLI puts it in user_request as "Generate a jenkins CI/CD pipeline for ..."
        user_request = getattr(state, "user_request", "") or ""
        user_request_lower = user_request.lower()

        if "jenkins" in user_request_lower:
            return "jenkins"
        if "gitlab_ci" in user_request_lower or "gitlab ci" in user_request_lower:
            return "gitlab_ci"
        if "github_actions" in user_request_lower or "github actions" in user_request_lower:
            return "github_actions"
        if "circleci" in user_request_lower or "circle ci" in user_request_lower:
            return "circleci"
        if "azure" in user_request_lower:
            return "azure_devops"

        # Priority 2 — if repo already has CI, use same platform
        if analysis.existing_ci.has_ci and analysis.existing_ci.platform:
            return analysis.existing_ci.platform

        # Priority 3 — auto-detect from repo URL
        if "github.com" in analysis.repo_url:
            return "github_actions"
        if "gitlab" in analysis.repo_url:
            return "gitlab_ci"

        # Priority 4 — default
        return "github_actions"

    def _build_stages(self, analysis: Any) -> list[PipelineStage]:
        """Build pipeline stages based on detected tech stack and extracted commands."""
        stages: list[PipelineStage] = []
        primary_lang = analysis.languages[0].name.lower() if analysis.languages else "python"

        # Get real extracted commands (set by RepoAnalysisAgent)
        extracted: dict = analysis.build_commands if analysis.build_commands else {}

        # Checkout stage (always first)
        stages.append(PipelineStage(
            name="Checkout",
            stage_type=StageType.CHECKOUT,
            commands=["checkout repository"],
        ))

        # Setup stage — runtime setup
        stages.append(PipelineStage(
            name=f"Setup {primary_lang.title()}",
            stage_type=StageType.SETUP,
            commands=[f"setup {primary_lang} runtime"],
        ))

        # Install Dependencies
        install_cmds = extracted.get("install") or []
        if not install_cmds and primary_lang in STAGE_TEMPLATES:
            # Fall back to template
            for t in STAGE_TEMPLATES[primary_lang]:
                if t["type"] == StageType.INSTALL:
                    install_cmds = t["commands"]
                    break
        if install_cmds:
            stages.append(PipelineStage(
                name="Install Dependencies",
                stage_type=StageType.INSTALL,
                commands=install_cmds,
            ))

        # Lint
        lint_cmds = extracted.get("lint") or []
        if not lint_cmds and primary_lang in STAGE_TEMPLATES:
            for t in STAGE_TEMPLATES[primary_lang]:
                if t["type"] == StageType.LINT:
                    lint_cmds = t["commands"]
                    break
        if lint_cmds:
            stages.append(PipelineStage(
                name="Lint",
                stage_type=StageType.LINT,
                commands=lint_cmds,
                continue_on_error=True,
            ))

        # Test
        test_cmds = extracted.get("test") or []
        if not test_cmds and primary_lang in STAGE_TEMPLATES:
            for t in STAGE_TEMPLATES[primary_lang]:
                if t["type"] == StageType.TEST:
                    test_cmds = t["commands"]
                    break
        if test_cmds:
            stages.append(PipelineStage(
                name="Test",
                stage_type=StageType.TEST,
                commands=test_cmds,
            ))

        # Build (JS/TS only or explicit build command)
        build_cmds = extracted.get("build") or []
        if not build_cmds and primary_lang in STAGE_TEMPLATES:
            for t in STAGE_TEMPLATES[primary_lang]:
                if t["type"] == StageType.BUILD:
                    build_cmds = t["commands"]
                    break
        if build_cmds:
            stages.append(PipelineStage(
                name="Build",
                stage_type=StageType.BUILD,
                commands=build_cmds,
            ))

        # Docker build/push stage (if Dockerfile detected)
        if analysis.containerization.has_dockerfile:
            stages.append(PipelineStage(
                name="Docker Build",
                stage_type=StageType.DOCKER_BUILD,
                commands=["docker build -t $IMAGE_NAME ."],
            ))
            stages.append(PipelineStage(
                name="Docker Push",
                stage_type=StageType.DOCKER_PUSH,
                commands=["docker push $IMAGE_NAME"],
                depends_on=["Docker Build"],
            ))

        # Deployment stage
        if analysis.infrastructure.has_kubernetes:
            stages.append(PipelineStage(
                name="Deploy to Kubernetes",
                stage_type=StageType.DEPLOY,
                commands=["kubectl apply -f k8s/"],
                depends_on=["Docker Push"] if analysis.containerization.has_dockerfile else [],
            ))
        elif analysis.infrastructure.has_terraform:
            stages.append(PipelineStage(
                name="Terraform Apply",
                stage_type=StageType.DEPLOY,
                commands=["terraform init", "terraform plan", "terraform apply -auto-approve"],
            ))

        return stages

    def _determine_deployment_strategy(self, analysis: Any) -> DeploymentStrategy:
        """Determine the deployment strategy."""
        if analysis.infrastructure.has_kubernetes:
            return DeploymentStrategy.ROLLING
        return DeploymentStrategy.RECREATE

    def _configure_environments(self, analysis: Any) -> list[Environment]:
        """Configure deployment environments."""
        environments = [
            Environment(name="development", auto_deploy=True),
            Environment(name="staging", auto_deploy=True, requires_approval=False),
            Environment(name="production", requires_approval=True, auto_deploy=False),
        ]

        # Set cloud provider if detected
        if analysis.infrastructure.cloud_provider:
            for env in environments:
                env.cloud_provider = analysis.infrastructure.cloud_provider

        return environments

    def _identify_secrets(self, analysis: Any) -> list[SecretConfig]:
        """Identify required secrets for the pipeline."""
        secrets: list[SecretConfig] = []

        if analysis.containerization.has_dockerfile:
            secrets.extend([
                SecretConfig(name="DOCKER_USERNAME", description="Docker registry username"),
                SecretConfig(name="DOCKER_PASSWORD", description="Docker registry password"),
            ])

        if analysis.infrastructure.has_terraform:
            secrets.extend([
                SecretConfig(name="AWS_ACCESS_KEY_ID", description="AWS access key"),
                SecretConfig(name="AWS_SECRET_ACCESS_KEY", description="AWS secret key"),
            ])

        if analysis.infrastructure.has_kubernetes:
            secrets.append(
                SecretConfig(name="KUBECONFIG", description="Kubernetes config")
            )

        return secrets

    def _configure_approval_gates(self, state: PipelineState) -> list[ApprovalGate]:
        """Configure approval gates."""
        if not state.requires_approval:
            return []

        return [
            ApprovalGate(
                stage="Deploy to Production",
                required_approvals=1,
                auto_approve_after_minutes=60,
            )
        ]

    def _estimate_duration(self, stages: list[PipelineStage]) -> int:
        """Estimate pipeline duration in minutes."""
        # Rough estimate: 2 min per stage + extra for build/deploy
        base = len(stages) * 2
        for stage in stages:
            if stage.stage_type in (StageType.BUILD, StageType.DOCKER_BUILD):
                base += 5
            elif stage.stage_type == StageType.DEPLOY:
                base += 3
            elif stage.stage_type == StageType.TEST:
                base += 3
        return base

    def _determine_caching(self, analysis: Any) -> dict[str, str]:
        """Determine caching strategy."""
        cache = {}

        for manager in analysis.package_managers:
            if manager in ("npm", "yarn", "pnpm"):
                cache["node_modules"] = "~/.npm"
            elif manager in ("pip", "poetry/pip", "pipenv"):
                cache["pip"] = "~/.cache/pip"
            elif manager == "go modules":
                cache["go"] = "~/go/pkg/mod"
            elif manager in ("maven", "gradle"):
                cache["java"] = "~/.m2/repository"
            elif manager == "cargo":
                cache["cargo"] = "~/.cargo"

        return cache