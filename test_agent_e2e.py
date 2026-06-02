"""
End-to-End Test: Run the CIForge Agent pipeline on local test repositories.

Tests the full agent pipeline (Repo Analysis → Planner → Generator → Validator)
against three different tech stacks without needing LLMs or external services.

Usage:
    python test_agent_e2e.py
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from src.agents.pipeline_generator import PipelineGeneratorAgent
from src.agents.planner import PlannerAgent
from src.agents.repo_analysis import RepoAnalysisAgent
from src.agents.validation import ValidationAgent
from src.models import PipelineState

console = Console()

# ─────────────────────────────────────────────────────────────────────
# Test repos (local paths)
# ─────────────────────────────────────────────────────────────────────
TEST_REPOS = {
    "Flask App (Python + Docker)": str(Path(__file__).parent / "test_repos" / "flask_app"),
    "Express API (Node.js)": str(Path(__file__).parent / "test_repos" / "node_app"),
    "Go API (Go + Docker + K8s)": str(Path(__file__).parent / "test_repos" / "go_app"),
}


# ─────────────────────────────────────────────────────────────────────
# Scoring rubric
# ─────────────────────────────────────────────────────────────────────
class ScoreCard:
    """Track evaluation metrics for each test repo."""

    def __init__(self, repo_name: str):
        self.repo_name = repo_name
        self.checks: list[tuple[str, bool, str]] = []  # (check_name, passed, detail)

    def check(self, name: str, passed: bool, detail: str = ""):
        self.checks.append((name, passed, detail))

    @property
    def score(self) -> tuple[int, int]:
        passed = sum(1 for _, p, _ in self.checks if p)
        return passed, len(self.checks)

    @property
    def percentage(self) -> float:
        p, t = self.score
        return (p / t * 100) if t > 0 else 0


async def run_pipeline(repo_name: str, repo_path: str) -> tuple[PipelineState, float]:
    """Run the full 4-agent pipeline on a local repo and return final state + duration."""

    state = PipelineState(
        user_request=f"Generate a GitHub Actions CI/CD pipeline for {repo_name}",
        repo_url=f"https://github.com/test/{repo_name.lower().replace(' ', '-')}",
        repo_local_path=repo_path,
        requires_approval=False,
        approved=True,
        session_id="test-001",
    )

    agents = [
        ("Repo Analysis", RepoAnalysisAgent()),
        ("Planner", PlannerAgent()),
        ("Pipeline Generator", PipelineGeneratorAgent()),
        ("Validator", ValidationAgent()),
    ]

    start = time.monotonic()
    for agent_name, agent in agents:
        console.print(f"  [dim]Running {agent_name}...[/dim]")
        state = await agent.execute(state)
    duration = time.monotonic() - start

    return state, duration


def evaluate_flask_app(state: PipelineState) -> ScoreCard:
    """Evaluate agent output against expected results for the Flask app."""
    sc = ScoreCard("Flask App (Python + Docker)")
    analysis = state.repo_analysis
    plan = state.pipeline_plan
    pipeline = state.generated_pipeline
    validation = state.validation_report

    # ── Repo Analysis checks ──
    lang_names = [l.name for l in analysis.languages] if analysis else []
    sc.check("Detected Python", "Python" in lang_names, f"Languages: {lang_names}")
    sc.check("Detected pip/poetry", any(m in (analysis.package_managers or []) for m in ["pip", "poetry/pip"]),
             f"Managers: {analysis.package_managers if analysis else []}")
    sc.check("Detected Flask framework", "Flask" in (analysis.frameworks or []),
             f"Frameworks: {analysis.frameworks if analysis else []}")
    sc.check("Detected Dockerfile", analysis.containerization.has_dockerfile if analysis else False,
             f"Dockerfile: {analysis.containerization.has_dockerfile if analysis else 'N/A'}")
    sc.check("Detected Docker Compose", analysis.containerization.has_compose if analysis else False,
             f"Compose: {analysis.containerization.has_compose if analysis else 'N/A'}")
    sc.check("Detected multi-stage build", analysis.containerization.multi_stage if analysis else False,
             f"Multi-stage: {analysis.containerization.multi_stage if analysis else 'N/A'}")
    sc.check("Detected pytest", "pytest" in (analysis.test_frameworks or []),
             f"Test frameworks: {analysis.test_frameworks if analysis else []}")

    # ── Planner checks ──
    sc.check("Plan created", plan is not None)
    if plan:
        stage_types = [s.stage_type.value for s in plan.stages]
        sc.check("Has install stage", "install" in stage_types, f"Stages: {stage_types}")
        sc.check("Has test stage", "test" in stage_types, f"Stages: {stage_types}")
        sc.check("Has docker_build stage", "docker_build" in stage_types, f"Stages: {stage_types}")
        sc.check("Platform is github_actions", plan.target_platform == "github_actions",
                 f"Platform: {plan.target_platform}")

    # ── Generator checks ──
    sc.check("Pipeline generated", pipeline is not None and len(pipeline.files) > 0)
    if pipeline and pipeline.files:
        primary = pipeline.files[0]
        sc.check("Output is .github/workflows/*.yml", ".github/workflows" in primary.path,
                 f"Path: {primary.path}")
        config = yaml.safe_load(primary.content)
        sc.check("Has 'name' field", "name" in config)
        sc.check("Has 'on' triggers", "on" in config)
        jobs = config.get("jobs", {})
        sc.check("Has CI job", "ci" in jobs, f"Jobs: {list(jobs.keys())}")
        sc.check("Has Docker job", "docker" in jobs, f"Jobs: {list(jobs.keys())}")

        # Check CI steps use correct actions
        if "ci" in jobs:
            steps = jobs["ci"].get("steps", [])
            step_uses = [s.get("uses", "") for s in steps]
            sc.check("Uses actions/checkout@v4",
                     any("actions/checkout" in u for u in step_uses),
                     f"Step uses: {step_uses}")
            sc.check("Uses actions/setup-python",
                     any("actions/setup-python" in u for u in step_uses),
                     f"Step uses: {step_uses}")

    # ── Validation checks ──
    sc.check("Validation ran", validation is not None)
    if validation:
        sc.check("Validation passed", validation.passed, f"Issues: {len(validation.issues)}")
        sc.check("Syntax valid", validation.syntax_valid)
        sc.check("Semantic valid", validation.semantic_valid)
        sc.check("Security passed", validation.security_passed)

    return sc


def evaluate_node_app(state: PipelineState) -> ScoreCard:
    """Evaluate agent output against expected results for the Node.js app."""
    sc = ScoreCard("Express API (Node.js)")
    analysis = state.repo_analysis
    plan = state.pipeline_plan
    pipeline = state.generated_pipeline
    validation = state.validation_report

    # ── Repo Analysis checks ──
    lang_names = [l.name for l in analysis.languages] if analysis else []
    sc.check("Detected JavaScript", "JavaScript" in lang_names, f"Languages: {lang_names}")
    sc.check("Detected npm", "npm" in (analysis.package_managers or []),
             f"Managers: {analysis.package_managers if analysis else []}")
    sc.check("Detected Jest", "Jest" in (analysis.test_frameworks or []),
             f"Test frameworks: {analysis.test_frameworks if analysis else []}")
    sc.check("No Dockerfile detected", not (analysis.containerization.has_dockerfile if analysis else True))

    # ── Planner checks ──
    sc.check("Plan created", plan is not None)
    if plan:
        stage_types = [s.stage_type.value for s in plan.stages]
        sc.check("Has install stage", "install" in stage_types, f"Stages: {stage_types}")
        sc.check("Has lint stage", "lint" in stage_types, f"Stages: {stage_types}")
        sc.check("Has test stage", "test" in stage_types, f"Stages: {stage_types}")
        sc.check("Has build stage", "build" in stage_types, f"Stages: {stage_types}")
        sc.check("No docker_build (no Dockerfile)", "docker_build" not in stage_types, f"Stages: {stage_types}")

    # ── Generator checks ──
    sc.check("Pipeline generated", pipeline is not None and len(pipeline.files) > 0)
    if pipeline and pipeline.files:
        primary = pipeline.files[0]
        config = yaml.safe_load(primary.content)
        jobs = config.get("jobs", {})
        sc.check("Has CI job", "ci" in jobs, f"Jobs: {list(jobs.keys())}")
        sc.check("No Docker job (no Dockerfile)", "docker" not in jobs, f"Jobs: {list(jobs.keys())}")

        if "ci" in jobs:
            steps = jobs["ci"].get("steps", [])
            step_uses = [s.get("uses", "") for s in steps]
            sc.check("Uses actions/setup-node",
                     any("actions/setup-node" in u for u in step_uses),
                     f"Step uses: {step_uses}")
            step_runs = [s.get("run", "") for s in steps]
            sc.check("Has npm ci command", any("npm ci" in r for r in step_runs),
                     f"Step runs: {step_runs}")

    # ── Validation checks ──
    sc.check("Validation ran", validation is not None)
    if validation:
        sc.check("Validation passed", validation.passed)
        sc.check("Syntax valid", validation.syntax_valid)
        sc.check("Security passed", validation.security_passed)

    return sc


def evaluate_go_app(state: PipelineState) -> ScoreCard:
    """Evaluate agent output against expected results for the Go app."""
    sc = ScoreCard("Go API (Go + Docker + K8s)")
    analysis = state.repo_analysis
    plan = state.pipeline_plan
    pipeline = state.generated_pipeline
    validation = state.validation_report

    # ── Repo Analysis checks ──
    lang_names = [l.name for l in analysis.languages] if analysis else []
    sc.check("Detected Go", "Go" in lang_names, f"Languages: {lang_names}")
    sc.check("Detected go modules", "go modules" in (analysis.package_managers or []),
             f"Managers: {analysis.package_managers if analysis else []}")
    sc.check("Detected Dockerfile", analysis.containerization.has_dockerfile if analysis else False)
    sc.check("Detected multi-stage Docker", analysis.containerization.multi_stage if analysis else False)
    sc.check("Detected Kubernetes", analysis.infrastructure.has_kubernetes if analysis else False,
             f"K8s: {analysis.infrastructure.has_kubernetes if analysis else 'N/A'}")
    sc.check("Detected K8s manifests", len(analysis.infrastructure.k8s_manifest_paths or []) > 0,
             f"Paths: {analysis.infrastructure.k8s_manifest_paths if analysis else []}")

    # ── Planner checks ──
    sc.check("Plan created", plan is not None)
    if plan:
        stage_types = [s.stage_type.value for s in plan.stages]
        sc.check("Has test stage", "test" in stage_types, f"Stages: {stage_types}")
        sc.check("Has docker_build stage", "docker_build" in stage_types, f"Stages: {stage_types}")
        sc.check("Has deploy stage", "deploy" in stage_types, f"Stages: {stage_types}")

    # ── Generator checks ──
    sc.check("Pipeline generated", pipeline is not None and len(pipeline.files) > 0)
    if pipeline and pipeline.files:
        primary = pipeline.files[0]
        config = yaml.safe_load(primary.content)
        jobs = config.get("jobs", {})
        sc.check("Has CI job", "ci" in jobs, f"Jobs: {list(jobs.keys())}")
        sc.check("Has Docker job", "docker" in jobs, f"Jobs: {list(jobs.keys())}")
        sc.check("Has Deploy job", "deploy" in jobs, f"Jobs: {list(jobs.keys())}")

        if "ci" in jobs:
            steps = jobs["ci"].get("steps", [])
            step_uses = [s.get("uses", "") for s in steps]
            sc.check("Uses actions/setup-go",
                     any("actions/setup-go" in u for u in step_uses),
                     f"Step uses: {step_uses}")

        if "deploy" in jobs:
            deploy_steps = jobs["deploy"].get("steps", [])
            deploy_runs = [s.get("run", "") for s in deploy_steps]
            sc.check("Deploy uses kubectl",
                     any("kubectl" in r for r in deploy_runs),
                     f"Deploy runs: {deploy_runs}")

    # ── Validation checks ──
    sc.check("Validation ran", validation is not None)
    if validation:
        sc.check("Validation passed", validation.passed)
        sc.check("Syntax valid", validation.syntax_valid)
        sc.check("Security passed", validation.security_passed)

    return sc


def print_scorecard(sc: ScoreCard):
    """Print a detailed scorecard."""
    table = Table(title=f"Scorecard: {sc.repo_name}", show_header=True)
    table.add_column("Check", style="bold", min_width=30)
    table.add_column("Result", justify="center", min_width=8)
    table.add_column("Details", max_width=60)

    for name, passed, detail in sc.checks:
        icon = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        table.add_row(name, icon, detail[:60] if detail else "")

    console.print(table)
    p, t = sc.score
    pct = sc.percentage
    color = "green" if pct >= 80 else "yellow" if pct >= 60 else "red"
    console.print(f"  Score: [{color}]{p}/{t} ({pct:.0f}%)[/{color}]\n")


def print_generated_pipeline(state: PipelineState, repo_name: str):
    """Print the generated pipeline YAML."""
    if state.generated_pipeline and state.generated_pipeline.files:
        for f in state.generated_pipeline.files:
            console.print(Panel(
                Syntax(f.content, "yaml", theme="monokai", line_numbers=True),
                title=f"[bold cyan]{repo_name} → {f.path}[/bold cyan]",
                subtitle=f.description,
                border_style="cyan",
            ))


async def main():
    console.print(Panel.fit(
        "[bold blue]CIForge Agent — End-to-End Test Suite[/bold blue]\n"
        "Testing the full pipeline on 3 sample repositories",
        border_style="blue",
    ))
    console.print()

    evaluators = {
        "Flask App (Python + Docker)": evaluate_flask_app,
        "Express API (Node.js)": evaluate_node_app,
        "Go API (Go + Docker + K8s)": evaluate_go_app,
    }

    scorecards: list[ScoreCard] = []

    for repo_name, repo_path in TEST_REPOS.items():
        console.rule(f"[bold]{repo_name}[/bold]")

        # Verify path exists
        if not os.path.isdir(repo_path):
            console.print(f"[red]Directory not found: {repo_path}[/red]")
            continue

        # Run pipeline
        try:
            state, duration = await run_pipeline(repo_name, repo_path)
            console.print(f"  [green]Pipeline completed in {duration:.2f}s[/green]\n")
        except Exception as e:
            console.print(f"  [bold red]Pipeline failed: {e}[/bold red]\n")
            import traceback
            traceback.print_exc()
            continue

        # Show generated pipeline
        print_generated_pipeline(state, repo_name)

        # Evaluate
        evaluator = evaluators[repo_name]
        sc = evaluator(state)
        print_scorecard(sc)
        scorecards.append(sc)

    # ── Final Summary ──
    console.rule("[bold]Overall Summary[/bold]")
    summary = Table(title="Agent Performance Summary", show_header=True)
    summary.add_column("Repository", style="bold")
    summary.add_column("Score", justify="center")
    summary.add_column("Percentage", justify="center")

    total_passed = 0
    total_checks = 0
    for sc in scorecards:
        p, t = sc.score
        total_passed += p
        total_checks += t
        pct = sc.percentage
        color = "green" if pct >= 80 else "yellow" if pct >= 60 else "red"
        summary.add_row(sc.repo_name, f"{p}/{t}", f"[{color}]{pct:.0f}%[/{color}]")

    if total_checks > 0:
        overall_pct = total_passed / total_checks * 100
        color = "green" if overall_pct >= 80 else "yellow" if overall_pct >= 60 else "red"
        summary.add_row(
            "[bold]OVERALL[/bold]",
            f"[bold]{total_passed}/{total_checks}[/bold]",
            f"[bold {color}]{overall_pct:.0f}%[/bold {color}]",
        )

    console.print(summary)
    console.print()

    if overall_pct >= 80:
        console.print(Panel("[bold green]Agent performs well across test repositories![/bold green]"))
    elif overall_pct >= 60:
        console.print(Panel("[bold yellow]Agent performs adequately but has room for improvement.[/bold yellow]"))
    else:
        console.print(Panel("[bold red]Agent needs significant improvements.[/bold red]"))


if __name__ == "__main__":
    asyncio.run(main())
