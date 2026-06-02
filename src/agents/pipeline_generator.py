"""
Pipeline Generation Agent — Produces actual CI/CD configuration files.

Takes a PipelinePlan and generates platform-specific CI/CD configs:
- GitHub Actions workflows (.github/workflows/*.yml)
- GitLab CI (.gitlab-ci.yml)
- Jenkins (Jenkinsfile)

Uses a hybrid template + LLM approach for generation.
"""

from __future__ import annotations

from typing import Any

import structlog
import yaml

from src.agents.base import BaseAgent
from src.models import (
    GeneratedFile,
    PipelineConfig,
    PipelineState,
    StageType,
)

logger = structlog.get_logger()


# ==============================================================================
# YAML block scalar representer — forces multiline strings to use | notation
# ==============================================================================

class _LiteralStr(str):
    """Marker class to force YAML literal block scalar output."""
    pass


def _literal_representer(dumper: yaml.Dumper, data: str) -> yaml.ScalarNode:
    """Represent strings with newlines as YAML literal block scalars (|)."""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, _literal_representer)
yaml.add_representer(_LiteralStr, _literal_representer)


class PipelineGeneratorAgent(BaseAgent):
    """
    Generates CI/CD pipeline configuration files from a PipelinePlan.

    Hybrid approach:
    1. Use templates for common patterns
    2. Use LLM for novel/complex configurations
    3. Apply best practices (caching, matrix, artifacts)
    """

    def __init__(self) -> None:
        super().__init__(
            name="PipelineGeneratorAgent",
            description="Generates CI/CD pipeline configuration files",
        )

    async def execute(self, state: PipelineState) -> PipelineState:
        """Generate pipeline configuration files."""
        state.current_stage = "generating"

        if not state.pipeline_plan:
            raise ValueError("PipelinePlan is required. Run PlannerAgent first.")

        plan = state.pipeline_plan
        platform = plan.target_platform

        # Generate platform-specific config
        if platform == "github_actions":
            files = self._generate_github_actions(state)
        elif platform == "gitlab_ci":
            files = self._generate_gitlab_ci(state)
        elif platform == "jenkins":
            files = self._generate_jenkins(state)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

        state.generated_pipeline = PipelineConfig(
            files=files,
            platform=platform,
        )

        self._log(
            "pipeline_generated",
            platform=platform,
            num_files=len(files),
            files=[f.path for f in files],
        )

        return state

    # =========================================================================
    # GitHub Actions Generation
    # =========================================================================

    def _generate_github_actions(self, state: PipelineState) -> list[GeneratedFile]:
        """Generate GitHub Actions workflow files."""
        plan = state.pipeline_plan
        analysis = state.repo_analysis
        assert plan is not None
        assert analysis is not None

        files: list[GeneratedFile] = []

        # Build the main CI/CD workflow
        workflow = self._build_github_workflow(plan, analysis)
        workflow_yaml = yaml.dump(workflow, default_flow_style=False, sort_keys=False, width=float('inf'), allow_unicode=True)
        # PyYAML quotes 'on' as it's a YAML 1.1 keyword — restore it
        workflow_yaml = workflow_yaml.replace("'on':", "on:")

        files.append(GeneratedFile(
            path=".github/workflows/ci-cd.yml",
            content=workflow_yaml,
            description="Main CI/CD pipeline workflow",
            is_primary=True,
        ))

        return files

    def _build_github_workflow(self, plan: Any, analysis: Any) -> dict[str, Any]:
        """Build the GitHub Actions workflow dictionary."""
        primary_lang = analysis.languages[0].name.lower() if analysis.languages else "python"

        # Determine trigger events
        on_config: dict[str, Any] = {
            "push": {"branches": ["main", "master"]},
            "pull_request": {"branches": ["main", "master"]},
        }

        # Build jobs
        jobs: dict[str, Any] = {}

        # === CI Job (build + test) ===
        ci_steps = self._build_github_ci_steps(plan, analysis, primary_lang)
        ci_job: dict[str, Any] = {
            "name": "CI - Build & Test",
            "runs-on": "ubuntu-latest",
            "steps": ci_steps,
        }

        # Add caching
        if plan.caching_strategy:
            # Caching is handled within steps
            pass

        jobs["ci"] = ci_job

        # === Docker Build Job (if applicable) ===
        has_docker_stages = any(
            s.stage_type in (StageType.DOCKER_BUILD, StageType.DOCKER_PUSH)
            for s in plan.stages
        )
        if has_docker_stages:
            docker_steps = self._build_github_docker_steps(plan, analysis)
            jobs["docker"] = {
                "name": "Build & Push Docker Image",
                "runs-on": "ubuntu-latest",
                "needs": ["ci"],
                "if": "github.ref == 'refs/heads/main' && github.event_name == 'push'",
                "steps": docker_steps,
            }

        # === Deploy Job (if applicable) ===
        has_deploy = any(s.stage_type == StageType.DEPLOY for s in plan.stages)
        if has_deploy:
            deploy_steps = self._build_github_deploy_steps(plan, analysis)
            deploy_needs = ["ci"]
            if has_docker_stages:
                deploy_needs.append("docker")

            jobs["deploy"] = {
                "name": "Deploy",
                "runs-on": "ubuntu-latest",
                "needs": deploy_needs,
                "if": "github.ref == 'refs/heads/main' && github.event_name == 'push'",
                "environment": "production",
                "steps": deploy_steps,
            }

        env_vars = self._build_env_vars(analysis)

        workflow: dict[str, Any] = {
            "name": "CI/CD Pipeline",
            "on": on_config,
            "jobs": jobs,
        }

        # Only add env block if there are variables
        if env_vars:
            workflow["env"] = env_vars

        return workflow

    def _build_github_ci_steps(
        self, plan: Any, analysis: Any, primary_lang: str
    ) -> list[dict[str, Any]]:
        """Build CI steps for GitHub Actions."""
        steps: list[dict[str, Any]] = []

        # Checkout
        steps.append({
            "name": "Checkout code",
            "uses": "actions/checkout@v4",
        })

        # Language setup
        setup_step = self._get_language_setup_step(primary_lang, analysis)
        if setup_step:
            steps.append(setup_step)

        # Cache
        cache_step = self._get_cache_step(primary_lang)
        if cache_step:
            steps.append(cache_step)

        # Install, lint, test, build steps from plan
        for stage in plan.stages:
            if stage.stage_type in (StageType.CHECKOUT, StageType.SETUP):
                continue  # Already handled
            if stage.stage_type in (StageType.DOCKER_BUILD, StageType.DOCKER_PUSH, StageType.DEPLOY):
                continue  # Handled in separate jobs

            step: dict[str, Any] = {
                "name": stage.name,
                "run": "\n".join(stage.commands) + "\n" if len(stage.commands) > 1 else stage.commands[0],
            }
            if stage.continue_on_error:
                step["continue-on-error"] = True

            steps.append(step)

        return steps

    def _build_github_docker_steps(self, plan: Any, analysis: Any) -> list[dict[str, Any]]:
        """Build Docker build/push steps for GitHub Actions."""
        steps: list[dict[str, Any]] = [
            {"name": "Checkout code", "uses": "actions/checkout@v4"},
            {
                "name": "Set up Docker Buildx",
                "uses": "docker/setup-buildx-action@v3",
            },
            {
                "name": "Login to Docker Hub",
                "uses": "docker/login-action@v3",
                "with": {
                    "username": "${{ secrets.DOCKER_USERNAME }}",
                    "password": "${{ secrets.DOCKER_PASSWORD }}",
                },
            },
            {
                "name": "Build and push Docker image",
                "uses": "docker/build-push-action@v5",
                "with": {
                    "context": ".",
                    "push": True,
                    "tags": "${{ secrets.DOCKER_USERNAME }}/${{ github.event.repository.name }}:${{ github.sha }},${{ secrets.DOCKER_USERNAME }}/${{ github.event.repository.name }}:latest",
                    "cache-from": "type=gha",
                    "cache-to": "type=gha,mode=max",
                },
            },
        ]
        return steps

    def _build_github_deploy_steps(self, plan: Any, analysis: Any) -> list[dict[str, Any]]:
        """Build deployment steps for GitHub Actions."""
        steps: list[dict[str, Any]] = [
            {"name": "Checkout code", "uses": "actions/checkout@v4"},
        ]

        if analysis.infrastructure.has_kubernetes:
            steps.extend([
                {
                    "name": "Configure kubectl",
                    "uses": "azure/setup-kubectl@v3",
                },
                {
                    "name": "Set Kubernetes context",
                    "run": "echo \"${{ secrets.KUBECONFIG }}\" > kubeconfig.yml\nexport KUBECONFIG=kubeconfig.yml",
                },
                {
                    "name": "Deploy to Kubernetes",
                    "run": "kubectl apply -f k8s/\nkubectl rollout status deployment/app",
                },
            ])
        elif analysis.infrastructure.has_terraform:
            steps.extend([
                {
                    "name": "Setup Terraform",
                    "uses": "hashicorp/setup-terraform@v3",
                },
                {
                    "name": "Terraform Init",
                    "run": "terraform init",
                    "env": {
                        "AWS_ACCESS_KEY_ID": "${{ secrets.AWS_ACCESS_KEY_ID }}",
                        "AWS_SECRET_ACCESS_KEY": "${{ secrets.AWS_SECRET_ACCESS_KEY }}",
                    },
                },
                {
                    "name": "Terraform Plan",
                    "run": "terraform plan -out=tfplan",
                },
                {
                    "name": "Terraform Apply",
                    "run": "terraform apply -auto-approve tfplan",
                },
            ])

        return steps

    def _get_language_setup_step(self, lang: str, analysis: Any) -> dict[str, Any] | None:
        """Get the language setup action step."""
        setup_map: dict[str, dict[str, Any]] = {
            "python": {
                "name": "Set up Python",
                "uses": "actions/setup-python@v5",
                "with": {"python-version": "3.12"},
            },
            "javascript": {
                "name": "Set up Node.js",
                "uses": "actions/setup-node@v4",
                "with": {"node-version": "20", "cache": "npm"},
            },
            "typescript": {
                "name": "Set up Node.js",
                "uses": "actions/setup-node@v4",
                "with": {"node-version": "20", "cache": "npm"},
            },
            "go": {
                "name": "Set up Go",
                "uses": "actions/setup-go@v5",
                "with": {"go-version": "1.22"},
            },
            "java": {
                "name": "Set up JDK",
                "uses": "actions/setup-java@v4",
                "with": {"java-version": "21", "distribution": "temurin"},
            },
            "rust": {
                "name": "Set up Rust",
                "uses": "dtolnay/rust-toolchain@stable",
            },
        }
        return setup_map.get(lang)

    def _get_cache_step(self, lang: str) -> dict[str, Any] | None:
        """Get a caching step for the language."""
        cache_map: dict[str, dict[str, Any]] = {
            "python": {
                "name": "Cache pip dependencies",
                "uses": "actions/cache@v4",
                "with": {
                    "path": "~/.cache/pip",
                    "key": "${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}",
                    "restore-keys": "${{ runner.os }}-pip-",
                },
            },
            "go": {
                "name": "Cache Go modules",
                "uses": "actions/cache@v4",
                "with": {
                    "path": "~/go/pkg/mod",
                    "key": "${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}",
                    "restore-keys": "${{ runner.os }}-go-",
                },
            },
        }
        return cache_map.get(lang)

    def _build_env_vars(self, analysis: Any) -> dict[str, str]:
        """Build environment variables for the workflow."""
        env: dict[str, str] = {}

        if analysis.containerization.has_dockerfile:
            env["IMAGE_NAME"] = "${{ github.event.repository.name }}"

        return env

    # =========================================================================
    # GitLab CI Generation
    # =========================================================================

    def _generate_gitlab_ci(self, state: PipelineState) -> list[GeneratedFile]:
        """Generate GitLab CI configuration."""
        plan = state.pipeline_plan
        analysis = state.repo_analysis
        assert plan is not None
        assert analysis is not None

        primary_lang = analysis.languages[0].name.lower() if analysis.languages else "python"
        has_docker = analysis.containerization.has_dockerfile

        # Global image per language
        global_image_map: dict[str, str] = {
            "python": "python:3.12-slim",
            "javascript": "node:20-alpine",
            "typescript": "node:20-alpine",
            "go": "golang:1.22-alpine",
            "java": "maven:3.9-eclipse-temurin-21",
            "rust": "rust:1.77-slim",
            "ruby": "ruby:3.3-alpine",
        }
        global_image = global_image_map.get(primary_lang, "ubuntu:22.04")

        # Cache config per language
        cache_map: dict[str, dict[str, Any]] = {
            "python": {"key": "${CI_COMMIT_REF_SLUG}", "paths": [".cache/pip", "venv/"]},
            "javascript": {"key": "${CI_COMMIT_REF_SLUG}", "paths": ["node_modules/", ".npm/"]},
            "typescript": {"key": "${CI_COMMIT_REF_SLUG}", "paths": ["node_modules/", ".npm/"]},
            "go": {"key": "${CI_COMMIT_REF_SLUG}", "paths": ["$GOPATH/pkg/mod"]},
        }

        # Stages to skip — GitLab handles checkout automatically, image handles setup
        SKIP_STAGE_TYPES = {"checkout", "setup"}

        # Build stage list and jobs
        stage_names: list[str] = []
        jobs: dict[str, Any] = {}

        for stage in plan.stages:
            stage_key = stage.stage_type.value

            # Skip fake placeholder stages
            if stage_key in SKIP_STAGE_TYPES:
                continue

            if stage_key not in stage_names:
                stage_names.append(stage_key)

            job_name = stage.name.lower().replace(" ", "_")
            job: dict[str, Any] = {
                "stage": stage_key,
                "script": stage.commands,
            }

            # Docker build/push jobs need Docker-in-Docker
            if stage_key in ("docker_build", "docker_push"):
                job["image"] = "docker:24-cli"
                job["services"] = ["docker:24-dind"]
                job["variables"] = {
                    "DOCKER_TLS_CERTDIR": "/certs",
                    "DOCKER_IMAGE": "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA",
                }
                # Override with better commands
                if stage_key == "docker_build":
                    job["script"] = [
                        "docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY",
                        "docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .",
                        "docker build -t $CI_REGISTRY_IMAGE:latest .",
                    ]
                    job["only"] = ["main", "master"]
                elif stage_key == "docker_push":
                    job["script"] = [
                        "docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY",
                        "docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA",
                        "docker push $CI_REGISTRY_IMAGE:latest",
                    ]
                    job["only"] = ["main", "master"]
                    job["needs"] = ["docker_build"]

            # Deploy job — only on main branch, with kubectl image
            elif stage_key == "deploy":
                job["image"] = "bitnami/kubectl:latest"
                job["only"] = ["main", "master"]
                job["environment"] = {"name": "production"}
                job["script"] = [
                    "echo $KUBECONFIG_B64 | base64 -d > kubeconfig.yml",
                    "export KUBECONFIG=kubeconfig.yml",
                    "kubectl apply -f k8s/",
                    "kubectl rollout status deployment/app --timeout=120s",
                ]
                if stage.depends_on:
                    job["needs"] = [d.lower().replace(" ", "_") for d in stage.depends_on]

            # Lint — allow failure
            elif stage_key == "lint":
                job["allow_failure"] = True
                if stage.depends_on:
                    job["needs"] = [d.lower().replace(" ", "_") for d in stage.depends_on]

            else:
                if stage.depends_on:
                    job["needs"] = [d.lower().replace(" ", "_") for d in stage.depends_on]

            jobs[job_name] = job

        # Build the full config
        config: dict[str, Any] = {
            "image": global_image,
            "stages": stage_names,
        }

        # Add cache if applicable
        if primary_lang in cache_map:
            config["cache"] = cache_map[primary_lang]

        # Add Docker registry vars if Docker stages exist
        if has_docker:
            config["variables"] = {
                "CI_REGISTRY_IMAGE": "$CI_REGISTRY/$CI_PROJECT_PATH",
            }

        # Add workflow rules (skip duplicate pipelines)
        config["workflow"] = {
            "rules": [
                {"if": "$CI_PIPELINE_SOURCE == 'merge_request_event'"},
                {"if": "$CI_COMMIT_BRANCH"},
            ]
        }

        config.update(jobs)

        content = yaml.dump(
            config,
            default_flow_style=False,
            sort_keys=False,
            width=float("inf"),
            allow_unicode=True,
        )

        return [GeneratedFile(
            path=".gitlab-ci.yml",
            content=content,
            description="GitLab CI/CD pipeline configuration",
            is_primary=True,
        )]

    # =========================================================================
    # Jenkins Generation
    # =========================================================================

    def _generate_jenkins(self, state: PipelineState) -> list[GeneratedFile]:
        """Generate a production-grade Jenkinsfile."""
        plan = state.pipeline_plan
        analysis = state.repo_analysis
        assert plan is not None
        assert analysis is not None

        primary_lang = analysis.languages[0].name.lower() if analysis.languages else "python"
        has_docker = analysis.containerization.has_dockerfile
        has_k8s = analysis.infrastructure.has_kubernetes
        has_terraform = analysis.infrastructure.has_terraform

        # Stages to skip — Jenkins uses checkout scm and agent for these
        SKIP_STAGE_TYPES = {"checkout", "setup", "docker_build", "docker_push", "deploy"}

        # Build environment variables block
        env_vars: dict[str, str] = {}
        if has_docker:
            env_vars["DOCKER_IMAGE"] = "${env.DOCKER_REGISTRY}/${env.JOB_NAME.toLowerCase()}:${env.BUILD_NUMBER}"
            env_vars["DOCKER_REGISTRY"] = "docker.io"

        # Agent config per language
        agent_map = {
            "python": "    agent { docker { image 'python:3.12-slim' } }",
            "javascript": "    agent { docker { image 'node:20-alpine' } }",
            "typescript": "    agent { docker { image 'node:20-alpine' } }",
            "go": "    agent { docker { image 'golang:1.22-alpine' } }",
            "java": "    agent { docker { image 'maven:3.9-eclipse-temurin-21' } }",
            "rust": "    agent { docker { image 'rust:1.77-slim' } }",
        }
        agent_line = agent_map.get(primary_lang, "    agent any")

        lines: list[str] = ["pipeline {", agent_line, ""]

        # Environment block
        if env_vars:
            lines.append("    environment {")
            for k, v in env_vars.items():
                lines.append(f"        {k} = \"{v}\"")
            lines.append("    }")
            lines.append("")

        # Options
        lines.extend([
            "    options {",
            "        timeout(time: 30, unit: 'MINUTES')",
            "        buildDiscarder(logRotator(numToKeepStr: '10'))",
            "        disableConcurrentBuilds()",
            "    }",
            "",
            "    stages {",
        ])

        # Checkout stage — always use checkout scm
        lines.extend([
            "        stage('Checkout') {",
            "            steps {",
            "                checkout scm",
            "            }",
            "        }",
        ])

        # Language-specific setup for venv (Python only, others handled by Docker agent)
        if primary_lang == "python":
            lines.extend([
                "        stage('Setup') {",
                "            steps {",
                "                sh 'python3 -m venv venv'",
                "                sh '. venv/bin/activate'",
                "            }",
                "        }",
            ])

        # Regular stages (install, lint, test, build)
        for stage in plan.stages:
            if stage.stage_type.value in SKIP_STAGE_TYPES:
                continue
            if not stage.commands:
                continue

            lines.append(f"        stage('{stage.name}') {{")

            # Python commands need venv activation
            if primary_lang == "python" and stage.stage_type.value in ("install", "lint", "test"):
                lines.append("            steps {")
                full_cmd = " && ".join(stage.commands)
                lines.append(f"                sh '. venv/bin/activate && {full_cmd}'")
                lines.append("            }")
            else:
                lines.append("            steps {")
                for cmd in stage.commands:
                    lines.append(f"                sh '{cmd}'")
                lines.append("            }")

            lines.append("        }")

        # Docker Build & Push — only on main branch, with credentials
        if has_docker:
            lines.extend([
                "        stage('Docker Build') {",
                "            when { branch 'main' }",
                "            steps {",
                "                sh \"docker build -t ${DOCKER_IMAGE} .\"",
                "                sh \"docker tag ${DOCKER_IMAGE} ${DOCKER_REGISTRY}/${JOB_NAME.toLowerCase()}:latest\"",
                "            }",
                "        }",
                "        stage('Docker Push') {",
                "            when { branch 'main' }",
                "            steps {",
                "                withCredentials([usernamePassword(",
                "                    credentialsId: 'docker-hub-credentials',",
                "                    usernameVariable: 'DOCKER_USER',",
                "                    passwordVariable: 'DOCKER_PASS'",
                "                )]) {",
                "                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'",
                "                    sh \"docker push ${DOCKER_IMAGE}\"",
                "                    sh \"docker push ${DOCKER_REGISTRY}/${JOB_NAME.toLowerCase()}:latest\"",
                "                }",
                "            }",
                "        }",
            ])

        # Kubernetes Deploy
        if has_k8s:
            lines.extend([
                "        stage('Deploy to Kubernetes') {",
                "            when { branch 'main' }",
                "            steps {",
                "                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {",
                "                    sh 'kubectl apply -f k8s/'",
                "                    sh 'kubectl rollout status deployment/app --timeout=120s'",
                "                }",
                "            }",
                "        }",
            ])

        # Terraform Deploy
        if has_terraform:
            lines.extend([
                "        stage('Terraform Apply') {",
                "            when { branch 'main' }",
                "            steps {",
                "                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',",
                "                    credentialsId: 'aws-credentials']]) {",
                "                    sh 'terraform init'",
                "                    sh 'terraform plan -out=tfplan'",
                "                    sh 'terraform apply -auto-approve tfplan'",
                "                }",
                "            }",
                "        }",
            ])

        # Close stages
        lines.extend([
            "    }",
            "",
            "    post {",
            "        always {",
            "            cleanWs()",
            "        }",
            "        success {",
            "            echo 'Pipeline succeeded!'",
            "        }",
            "        failure {",
            "            echo 'Pipeline failed!'",
            "        }",
            "    }",
            "}",
        ])

        content = "\n".join(lines) + "\n"

        return [GeneratedFile(
            path="Jenkinsfile",
            content=content,
            description="Jenkins declarative pipeline configuration",
            is_primary=True,
        )]

