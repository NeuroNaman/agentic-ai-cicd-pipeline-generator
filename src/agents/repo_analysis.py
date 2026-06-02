"""
Repository Analysis Agent — Deep inspection of repository structure, tech stack,
and deployment requirements.

Improvements:
- Better Docker detection (case-insensitive, any depth, compose variants)
- Real command extraction from package.json, pyproject.toml, Makefile
- Framework detection from package.json dependencies
- Monorepo detection (nx, turbo, pnpm workspaces, lerna)
- CI vs full CI/CD decision logic
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import structlog

from src.agents.base import BaseAgent
from src.models import (
    ContainerInfo,
    ExistingCIInfo,
    InfraInfo,
    LanguageInfo,
    PipelineState,
    RepoAnalysis,
    ServiceInfo,
)

logger = structlog.get_logger()

# ==============================================================================
# File extension → Language mapping
# ==============================================================================
EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JavaScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".scala": "Scala",
    ".r": "R",
    ".dart": "Dart",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".hs": "Haskell",
    ".lua": "Lua",
    ".sh": "Shell",
}

# ==============================================================================
# Package manifest → Package manager mapping
# ==============================================================================
PACKAGE_MANIFEST_MAP: dict[str, dict[str, str]] = {
    "package.json": {"manager": "npm", "language": "JavaScript"},
    "yarn.lock": {"manager": "yarn", "language": "JavaScript"},
    "pnpm-lock.yaml": {"manager": "pnpm", "language": "JavaScript"},
    "requirements.txt": {"manager": "pip", "language": "Python"},
    "Pipfile": {"manager": "pipenv", "language": "Python"},
    "pyproject.toml": {"manager": "poetry/pip", "language": "Python"},
    "setup.py": {"manager": "pip", "language": "Python"},
    "go.mod": {"manager": "go modules", "language": "Go"},
    "pom.xml": {"manager": "maven", "language": "Java"},
    "build.gradle": {"manager": "gradle", "language": "Java"},
    "build.gradle.kts": {"manager": "gradle", "language": "Kotlin"},
    "Cargo.toml": {"manager": "cargo", "language": "Rust"},
    "Gemfile": {"manager": "bundler", "language": "Ruby"},
    "composer.json": {"manager": "composer", "language": "PHP"},
    "pubspec.yaml": {"manager": "pub", "language": "Dart"},
    "mix.exs": {"manager": "mix", "language": "Elixir"},
}

# ==============================================================================
# Framework detection from config files
# ==============================================================================
FRAMEWORK_FILE_INDICATORS: dict[str, list[str]] = {
    "manage.py": ["Django"],
    "next.config.js": ["Next.js"],
    "next.config.mjs": ["Next.js"],
    "next.config.ts": ["Next.js"],
    "nuxt.config.js": ["Nuxt.js"],
    "nuxt.config.ts": ["Nuxt.js"],
    "angular.json": ["Angular"],
    "vue.config.js": ["Vue.js"],
    "svelte.config.js": ["SvelteKit"],
    "remix.config.js": ["Remix"],
    "gatsby-config.js": ["Gatsby"],
    "astro.config.mjs": ["Astro"],
    "nest-cli.json": ["NestJS"],
    "vite.config.ts": ["Vite"],
    "vite.config.js": ["Vite"],
    "webpack.config.js": ["Webpack"],
}

# Framework detection from package.json dependencies
FRAMEWORK_DEPENDENCY_MAP: dict[str, str] = {
    "next": "Next.js",
    "react": "React",
    "vue": "Vue.js",
    "@angular/core": "Angular",
    "nuxt": "Nuxt.js",
    "svelte": "Svelte",
    "@sveltejs/kit": "SvelteKit",
    "gatsby": "Gatsby",
    "remix": "Remix",
    "astro": "Astro",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "express": "Express.js",
    "koa": "Koa",
    "nestjs": "NestJS",
    "@nestjs/core": "NestJS",
    "vite": "Vite",
    "electron": "Electron",
}

# Python framework detection from import patterns
PYTHON_FRAMEWORK_IMPORTS: dict[str, str] = {
    "from fastapi": "FastAPI",
    "import fastapi": "FastAPI",
    "from flask": "Flask",
    "import flask": "Flask",
    "import django": "Django",
    "from django": "Django",
}

# ==============================================================================
# Test framework detection
# ==============================================================================
TEST_FRAMEWORK_INDICATORS: dict[str, str] = {
    "pytest.ini": "pytest",
    "jest.config.js": "Jest",
    "jest.config.ts": "Jest",
    "vitest.config.ts": "Vitest",
    "karma.conf.js": "Karma",
    ".mocharc.yml": "Mocha",
    "cypress.config.js": "Cypress",
    "cypress.config.ts": "Cypress",
    "playwright.config.ts": "Playwright",
}

# ==============================================================================
# CI/CD config detection
# ==============================================================================
CI_CONFIG_MAP: dict[str, str] = {
    ".github/workflows": "github_actions",
    ".gitlab-ci.yml": "gitlab_ci",
    "Jenkinsfile": "jenkins",
    ".circleci/config.yml": "circleci",
    "azure-pipelines.yml": "azure_devops",
    ".travis.yml": "travis_ci",
    "bitbucket-pipelines.yml": "bitbucket",
}

# ==============================================================================
# Monorepo detection files
# ==============================================================================
MONOREPO_INDICATORS: dict[str, str] = {
    "nx.json": "Nx",
    "turbo.json": "Turborepo",
    "pnpm-workspace.yaml": "pnpm workspaces",
    "pnpm-workspace.yml": "pnpm workspaces",
    "lerna.json": "Lerna",
    "rush.json": "Rush",
}


class RepoAnalysisAgent(BaseAgent):
    """
    Analyzes a repository to understand its structure, technology stack,
    and deployment requirements.
    """

    def __init__(self) -> None:
        super().__init__(
            name="RepoAnalysisAgent",
            description="Analyzes repository structure, tech stack, and deployment requirements",
        )

    async def execute(self, state: PipelineState) -> PipelineState:
        """Analyze the repository and update state with RepoAnalysis."""
        state.current_stage = "analyzing"

        repo_path = state.repo_local_path
        if not repo_path:
            repo_path = await self._clone_repo(state.repo_url)
            state.repo_local_path = repo_path

        file_tree = self._get_file_tree(Path(repo_path))
        state.repo_analysis = RepoAnalysis(
            repo_url=state.repo_url,
            repo_name=self._extract_repo_name(state.repo_url),
            raw_file_tree=file_tree,
        )

        # Run all analysis passes
        self._detect_languages(state.repo_analysis, Path(repo_path), file_tree)
        self._detect_package_managers(state.repo_analysis, file_tree)
        self._detect_frameworks(state.repo_analysis, Path(repo_path), file_tree)
        self._detect_test_frameworks(state.repo_analysis, Path(repo_path), file_tree)
        self._detect_containerization(state.repo_analysis, Path(repo_path), file_tree)
        self._detect_infrastructure(state.repo_analysis, file_tree)
        self._detect_existing_ci(state.repo_analysis, Path(repo_path), file_tree)
        self._detect_entry_points(state.repo_analysis, Path(repo_path), file_tree)
        self._detect_monorepo(state.repo_analysis, Path(repo_path), file_tree)
        self._extract_commands(state.repo_analysis, Path(repo_path), file_tree)

        self._log(
            "analysis_complete",
            languages=[lang.name for lang in state.repo_analysis.languages],
            frameworks=state.repo_analysis.frameworks,
            has_docker=state.repo_analysis.containerization.has_dockerfile,
            has_compose=state.repo_analysis.containerization.has_compose,
            has_k8s=state.repo_analysis.infrastructure.has_kubernetes,
            is_monorepo=state.repo_analysis.is_mono_repo,
            monorepo_tool=state.repo_analysis.monorepo_tool,
            extracted_commands=state.repo_analysis.build_commands,
        )

        return state

    async def _clone_repo(self, repo_url: str) -> str:
        import tempfile
        from git import Repo
        temp_dir = tempfile.mkdtemp(prefix="cicd_agent_")
        self._log("cloning_repo", url=repo_url, dest=temp_dir)
        Repo.clone_from(repo_url, temp_dir, depth=1)
        return temp_dir

    def _extract_repo_name(self, repo_url: str) -> str:
        name = repo_url.rstrip("/").split("/")[-1]
        if name.endswith(".git"):
            name = name[:-4]
        return name

    def _get_file_tree(self, repo_path: Path, max_depth: int = 6) -> list[str]:
        files: list[str] = []
        ignore_dirs = {
            ".git", "node_modules", "__pycache__", ".venv", "venv",
            ".tox", "dist", "build", ".next", ".turbo", ".nx",
            "coverage", ".nyc_output", "target",
        }

        for root, dirs, filenames in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            rel_root = Path(root).relative_to(repo_path)
            depth = len(rel_root.parts)
            if depth > max_depth:
                continue
            for filename in filenames:
                rel_path = rel_root / filename
                # Normalize to forward slashes for consistent matching
                files.append(rel_path.as_posix() if str(rel_root) != "." else filename)

        return sorted(files)

    # ==========================================================================
    # Language Detection
    # ==========================================================================

    def _detect_languages(self, analysis: RepoAnalysis, repo_path: Path, file_tree: list[str]) -> None:
        lang_counts: dict[str, int] = {}
        total = 0
        for file_path in file_tree:
            ext = Path(file_path).suffix.lower()
            if ext in EXTENSION_LANGUAGE_MAP:
                lang = EXTENSION_LANGUAGE_MAP[ext]
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
                total += 1

        if total > 0:
            analysis.languages = [
                LanguageInfo(name=lang, percentage=round((count / total) * 100, 1))
                for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1])
            ]

    # ==========================================================================
    # Package Manager Detection
    # ==========================================================================

    def _detect_package_managers(self, analysis: RepoAnalysis, file_tree: list[str]) -> None:
        managers = set()
        for file_path in file_tree:
            filename = Path(file_path).name
            if filename in PACKAGE_MANIFEST_MAP:
                managers.add(PACKAGE_MANIFEST_MAP[filename]["manager"])

        # Prefer yarn/pnpm over npm if lockfiles present
        if "yarn" in managers:
            managers.discard("npm")
        if "pnpm" in managers:
            managers.discard("npm")
            managers.discard("yarn")

        analysis.package_managers = sorted(managers)

    # ==========================================================================
    # Framework Detection (file-based + dependency-based + import-based)
    # ==========================================================================

    def _detect_frameworks(self, analysis: RepoAnalysis, repo_path: Path, file_tree: list[str]) -> None:
        frameworks: set[str] = set()

        # 1. File-based detection
        for file_path in file_tree:
            filename = Path(file_path).name
            if filename in FRAMEWORK_FILE_INDICATORS:
                frameworks.update(FRAMEWORK_FILE_INDICATORS[filename])

        # 2. package.json dependency-based detection (most reliable for JS/TS)
        pkg_json_path = self._find_file(repo_path, file_tree, "package.json")
        if pkg_json_path:
            try:
                pkg_data = json.loads(pkg_json_path.read_text(encoding="utf-8", errors="ignore"))
                all_deps = {
                    **pkg_data.get("dependencies", {}),
                    **pkg_data.get("devDependencies", {}),
                }
                for dep, framework in FRAMEWORK_DEPENDENCY_MAP.items():
                    if dep in all_deps:
                        frameworks.add(framework)
                        # If Next.js, remove plain React (it's implied)
                        if framework == "Next.js" and "React" in frameworks:
                            frameworks.discard("React")
            except Exception:
                pass

        # 3. Python import-based detection (check app.py, main.py, __init__.py)
        py_entry_files = ["app.py", "main.py", "server.py", "application.py", "__init__.py"]
        for entry in py_entry_files:
            found = self._find_file(repo_path, file_tree, entry)
            if found:
                try:
                    content = found.read_text(encoding="utf-8", errors="ignore").lower()
                    for pattern, fw in PYTHON_FRAMEWORK_IMPORTS.items():
                        if pattern in content:
                            frameworks.add(fw)
                except Exception:
                    pass

        # Remove generic "TypeScript" if real frameworks found
        if len(frameworks) > 1 and "TypeScript" in frameworks:
            frameworks.discard("TypeScript")

        analysis.frameworks = sorted(frameworks)

    # ==========================================================================
    # Test Framework Detection
    # ==========================================================================

    def _detect_test_frameworks(self, analysis: RepoAnalysis, repo_path: Path, file_tree: list[str]) -> None:
        test_frameworks: set[str] = set()

        for file_path in file_tree:
            filename = Path(file_path).name
            if filename in TEST_FRAMEWORK_INDICATORS:
                test_frameworks.add(TEST_FRAMEWORK_INDICATORS[filename])

        # Check package.json for test runner config
        pkg_json_path = self._find_file(repo_path, file_tree, "package.json")
        if pkg_json_path:
            try:
                pkg_data = json.loads(pkg_json_path.read_text(encoding="utf-8", errors="ignore"))
                all_deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                if "jest" in all_deps:
                    test_frameworks.add("Jest")
                if "vitest" in all_deps:
                    test_frameworks.add("Vitest")
                if "mocha" in all_deps:
                    test_frameworks.add("Mocha")
                if "cypress" in all_deps:
                    test_frameworks.add("Cypress")
                if "playwright" in all_deps or "@playwright/test" in all_deps:
                    test_frameworks.add("Playwright")
            except Exception:
                pass

        # File pattern detection
        for file_path in file_tree:
            if any(p in file_path.lower() for p in ["test", "spec", "__tests__"]):
                if file_path.endswith(".py"):
                    test_frameworks.add("pytest")
                elif file_path.endswith((".test.js", ".test.ts", ".spec.js", ".spec.ts")):
                    test_frameworks.add("Jest")

        analysis.test_frameworks = sorted(test_frameworks)

    # ==========================================================================
    # Docker / Containerization Detection (IMPROVED)
    # ==========================================================================

    def _detect_containerization(self, analysis: RepoAnalysis, repo_path: Path, file_tree: list[str]) -> None:
        container = ContainerInfo()
        has_dockerignore = False

        for file_path in file_tree:
            filename = Path(file_path).name
            filename_lower = filename.lower()

            # Dockerfile detection — case-insensitive, any name variant
            if (
                filename_lower == "dockerfile"
                or filename_lower.startswith("dockerfile.")
                or filename_lower.endswith(".dockerfile")
            ):
                container.has_dockerfile = True
                container.dockerfile_path = file_path
                self._parse_dockerfile(repo_path / Path(file_path), container)

            # docker-compose variants
            elif filename_lower in (
                "docker-compose.yml", "docker-compose.yaml",
                "docker-compose.prod.yml", "docker-compose.prod.yaml",
                "docker-compose.dev.yml", "docker-compose.dev.yaml",
                "docker-compose.staging.yml", "docker-compose.staging.yaml",
                "compose.yml", "compose.yaml",
            ):
                container.has_compose = True
                container.compose_path = file_path

            # .dockerignore — strong signal of Docker intent
            elif filename_lower == ".dockerignore":
                has_dockerignore = True

        # If .dockerignore exists but no Dockerfile found — project is Docker-intended.
        # Treat as has_dockerfile=True so Docker stages are generated.
        if has_dockerignore and not container.has_dockerfile:
            self._log(
                "docker_intent_detected",
                reason=".dockerignore found without Dockerfile — treating repo as Docker-enabled",
            )
            container.has_dockerfile = True
            container.dockerfile_path = "Dockerfile"  # Expected location

        analysis.containerization = container

    def _parse_dockerfile(self, dockerfile_path: Path, container: ContainerInfo) -> None:
        try:
            content = dockerfile_path.read_text(encoding="utf-8", errors="ignore")
            from_count = 0
            for line in content.splitlines():
                line = line.strip()
                if line.upper().startswith("FROM "):
                    from_count += 1
                    parts = line.split()
                    if len(parts) >= 2:
                        container.base_images.append(parts[1])
            container.multi_stage = from_count > 1
        except Exception:
            pass

    # ==========================================================================
    # Infrastructure Detection
    # ==========================================================================

    def _detect_infrastructure(self, analysis: RepoAnalysis, file_tree: list[str]) -> None:
        infra = InfraInfo()

        for file_path in file_tree:
            filename = Path(file_path).name.lower()
            path_lower = file_path.lower()

            if filename.endswith(".tf") or filename.endswith(".tf.json"):
                infra.has_terraform = True
            if filename in ("pulumi.yaml", "pulumi.yml"):
                infra.has_pulumi = True
            if filename == "samconfig.toml":
                infra.has_cloudformation = True
            if filename in ("playbook.yml", "playbook.yaml", "ansible.cfg"):
                infra.has_ansible = True

            # Kubernetes: check for k8s/kubernetes/kube directory OR kind/apiVersion in yaml
            if any(k in path_lower for k in ["k8s", "kubernetes", "kube", "manifests", "deploy"]):
                if filename.endswith((".yml", ".yaml")):
                    infra.has_kubernetes = True
                    infra.k8s_manifest_paths.append(file_path)

            if filename in ("chart.yaml", "chart.yml"):
                infra.has_helm = True
                infra.helm_chart_paths.append(str(Path(file_path).parent))

        analysis.infrastructure = infra

    # ==========================================================================
    # Monorepo Detection (NEW)
    # ==========================================================================

    def _detect_monorepo(self, analysis: RepoAnalysis, repo_path: Path, file_tree: list[str]) -> None:
        """Detect monorepo configurations."""
        monorepo_tool: str | None = None

        for file_path in file_tree:
            filename = Path(file_path).name
            if filename in MONOREPO_INDICATORS:
                monorepo_tool = MONOREPO_INDICATORS[filename]
                break

        # Also check package.json workspaces
        if not monorepo_tool:
            pkg_json_path = self._find_file(repo_path, file_tree, "package.json")
            if pkg_json_path:
                try:
                    pkg_data = json.loads(pkg_json_path.read_text(encoding="utf-8", errors="ignore"))
                    if "workspaces" in pkg_data:
                        monorepo_tool = "npm workspaces"
                except Exception:
                    pass

        # Store on analysis using proper model fields
        analysis.is_mono_repo = monorepo_tool is not None
        analysis.monorepo_tool = monorepo_tool

    # ==========================================================================
    # Real Command Extraction (NEW)
    # ==========================================================================

    def _extract_commands(self, analysis: RepoAnalysis, repo_path: Path, file_tree: list[str]) -> None:
        """
        Extract actual build/test/lint commands from package.json, pyproject.toml, Makefile.
        Stores results in analysis.build_commands dict.
        """
        commands: dict[str, list[str]] = {
            "install": [],
            "lint": [],
            "test": [],
            "build": [],
        }

        primary_lang = analysis.languages[0].name.lower() if analysis.languages else "python"

        # ---- JavaScript / TypeScript: parse package.json ----
        if primary_lang in ("javascript", "typescript"):
            pkg_json_path = self._find_file(repo_path, file_tree, "package.json")
            if pkg_json_path:
                try:
                    pkg_data = json.loads(pkg_json_path.read_text(encoding="utf-8", errors="ignore"))
                    scripts = pkg_data.get("scripts", {})

                    # Detect package manager
                    pm = "npm"
                    if any("yarn.lock" in f for f in file_tree):
                        pm = "yarn"
                    elif any("pnpm-lock.yaml" in f for f in file_tree):
                        pm = "pnpm"

                    run_prefix = f"{pm} run" if pm != "npm" else "npm run"
                    install_cmd = f"{pm} install" if pm != "npm" else "npm ci"

                    commands["install"] = [install_cmd]

                    # Map known script names → command categories
                    lint_scripts = ["lint", "eslint", "tslint", "check", "typecheck", "type-check"]
                    test_scripts = ["test", "test:ci", "test:coverage", "vitest", "jest"]
                    build_scripts = ["build", "build:prod", "compile", "bundle"]

                    for script in lint_scripts:
                        if script in scripts:
                            commands["lint"] = [f"{run_prefix} {script}"]
                            break

                    for script in test_scripts:
                        if script in scripts:
                            commands["test"] = [f"{run_prefix} {script}"]
                            break

                    for script in build_scripts:
                        if script in scripts:
                            commands["build"] = [f"{run_prefix} {script}"]
                            break

                except Exception:
                    pass

            # Fallback defaults
            if not commands["install"]:
                commands["install"] = ["npm ci"]
            if not commands["test"]:
                commands["test"] = ["npm test"]
            if not commands["build"]:
                commands["build"] = ["npm run build"]

        # ---- Python: parse pyproject.toml or setup.cfg ----
        elif primary_lang == "python":
            # Detect install command — use .cache/pip so GitLab cache actually works
            if any("requirements.txt" in f for f in file_tree):
                commands["install"] = ["pip install --cache-dir .cache/pip -r requirements.txt"]
            elif any("pyproject.toml" in f for f in file_tree):
                commands["install"] = ["pip install --cache-dir .cache/pip -e ."]
            elif any("setup.py" in f for f in file_tree):
                commands["install"] = ["pip install --cache-dir .cache/pip -e ."]
            else:
                commands["install"] = ["pip install --cache-dir .cache/pip -r requirements.txt"]

            # Check pyproject.toml for tool config
            pyproject_path = self._find_file(repo_path, file_tree, "pyproject.toml")
            if pyproject_path:
                try:
                    content = pyproject_path.read_text(encoding="utf-8", errors="ignore")
                    if "[tool.ruff]" in content or "ruff" in content:
                        commands["lint"] = ["ruff check .", "mypy ."]
                    elif "[tool.flake8]" in content or "flake8" in content:
                        commands["lint"] = ["flake8 ."]
                    if "[tool.pytest" in content or "pytest" in content:
                        commands["test"] = ["pytest --cov"]
                except Exception:
                    pass

            # Check Makefile for common targets
            makefile_path = self._find_file(repo_path, file_tree, "Makefile")
            if makefile_path:
                try:
                    make_content = makefile_path.read_text(encoding="utf-8", errors="ignore")
                    if re.search(r"^lint:", make_content, re.MULTILINE):
                        commands["lint"] = ["make lint"]
                    if re.search(r"^test:", make_content, re.MULTILINE):
                        commands["test"] = ["make test"]
                    if re.search(r"^build:", make_content, re.MULTILINE):
                        commands["build"] = ["make build"]
                except Exception:
                    pass

            # Defaults
            if not commands["lint"]:
                commands["lint"] = ["ruff check .", "mypy ."]
            if not commands["test"]:
                commands["test"] = ["pytest --cov"]

        # ---- Go ----
        elif primary_lang == "go":
            commands["install"] = ["go mod download"]
            commands["lint"] = ["golangci-lint run"]
            commands["test"] = ["go test ./..."]
            commands["build"] = ["go build -o app ./..."]

        # ---- Java ----
        elif primary_lang == "java":
            if any("pom.xml" in f for f in file_tree):
                commands["install"] = []
                commands["test"] = ["mvn clean verify"]
                commands["build"] = ["mvn package -DskipTests"]
            elif any("build.gradle" in f for f in file_tree):
                commands["test"] = ["./gradlew test"]
                commands["build"] = ["./gradlew build"]

        # ---- Rust ----
        elif primary_lang == "rust":
            commands["install"] = []
            commands["lint"] = ["cargo clippy -- -D warnings"]
            commands["test"] = ["cargo test"]
            commands["build"] = ["cargo build --release"]

        # ---- Ruby ----
        elif primary_lang == "ruby":
            commands["install"] = ["bundle install"]
            commands["lint"] = ["rubocop"]
            commands["test"] = ["bundle exec rspec"]

        # Store extracted commands on analysis object (proper Pydantic field)
        analysis.build_commands = commands

    # ==========================================================================
    # Existing CI Detection
    # ==========================================================================

    def _detect_existing_ci(self, analysis: RepoAnalysis, repo_path: Path, file_tree: list[str]) -> None:
        ci_info = ExistingCIInfo()
        for ci_path, platform in CI_CONFIG_MAP.items():
            matching = [f for f in file_tree if f.startswith(ci_path)]
            if matching:
                ci_info.has_ci = True
                ci_info.platform = platform
                ci_info.config_path = matching[0]
                try:
                    full_path = repo_path / Path(matching[0])
                    if full_path.is_file():
                        ci_info.config_content = full_path.read_text(encoding="utf-8", errors="ignore")[:5000]
                except Exception:
                    pass
                break
        analysis.existing_ci = ci_info

    # ==========================================================================
    # Entry Points
    # ==========================================================================

    def _detect_entry_points(self, analysis: RepoAnalysis, repo_path: Path, file_tree: list[str]) -> None:
        entry_point_patterns = {
            "main.py", "app.py", "server.py", "index.py",
            "index.js", "server.js", "app.js", "main.js",
            "index.ts", "server.ts", "app.ts", "main.ts",
            "main.go", "main.rs", "lib.rs",
        }
        analysis.entry_points = [
            f for f in file_tree if Path(f).name in entry_point_patterns
        ]

    # ==========================================================================
    # Helper: Find a file in the repo (handles subdirectories)
    # ==========================================================================

    def _find_file(self, repo_path: Path, file_tree: list[str], filename: str) -> Path | None:
        """Find a file by name in the file tree, returning the full path."""
        # Prefer root-level file first
        for f in file_tree:
            if Path(f).name == filename and "/" not in f and "\\" not in f:
                return repo_path / f
        # Then any depth
        for f in file_tree:
            if Path(f).name == filename:
                return repo_path / Path(f)
        return None
