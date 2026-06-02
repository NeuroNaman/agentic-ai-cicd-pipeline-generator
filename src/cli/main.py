"""
CLI — Command-line interface for the Agentic CI/CD Engineer.

Usage:
    cicd-agent generate <repo-url> [--platform github_actions] [--auto-approve]
    cicd-agent validate <repo-url>
    cicd-agent fix <repo-url> --logs <log-file>
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.syntax import Syntax

from src.config import CICDPlatform, get_settings

app = typer.Typer(
    name="cicd-agent",
    help="Agentic CI/CD Engineer — AI-powered pipeline generation and management",
    add_completion=False,
)
console = Console()


@app.command()
def generate(
    repo_url: str = typer.Argument(..., help="Repository URL to analyze and generate CI/CD for"),
    platform: str = typer.Option(
        "github_actions",
        "--platform", "-p",
        help="Target CI/CD platform",
    ),
    auto_approve: bool = typer.Option(
        False,
        "--auto-approve",
        help="Skip human approval gate",
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory for generated files (default: stdout)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Generate and validate without committing",
    ),
) -> None:
    """Generate a CI/CD pipeline for a repository."""
    console.print(Panel.fit(
        "[bold blue]Agentic CI/CD Engineer[/bold blue]\n"
        "AI-Powered Pipeline Generation",
        border_style="blue",
    ))

    console.print(f"\n[bold]Repository:[/bold] {repo_url}")
    console.print(f"[bold]Platform:[/bold] {platform}")
    console.print(f"[bold]Auto-approve:[/bold] {auto_approve}")
    console.print()

    asyncio.run(_run_generation(repo_url, platform, auto_approve, output_dir, dry_run))


async def _run_generation(
    repo_url: str,
    platform: str,
    auto_approve: bool,
    output_dir: str | None,
    dry_run: bool,
) -> None:
    """Run the full pipeline generation flow."""
    from src.agents.orchestrator import create_app
    from src.models import PipelineState

    session_id = str(uuid4())[:8]

    # Build initial state
    initial_state = PipelineState(
        user_request=f"Generate a {platform} CI/CD pipeline for {repo_url}",
        repo_url=repo_url,
        requires_approval=not auto_approve,
        approved=auto_approve,
        session_id=session_id,
        started_at=datetime.now(timezone.utc),
    ).model_dump()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Starting pipeline generation...", total=None)

        try:
            # Create and run the LangGraph app
            graph_app = create_app()

            progress.update(task, description="Analyzing repository...")
            result = await graph_app.ainvoke(initial_state)

            progress.update(task, description="Complete!")

        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {e}")
            raise typer.Exit(1)

    # Display results
    final_state = PipelineState(**result)
    _display_results(final_state, output_dir)


def _display_results(state: PipelineState, output_dir: str | None) -> None:
    """Display the generation results."""
    console.print()

    # Execution log
    if state.execution_logs:
        console.print("[bold]Execution Log:[/bold]")
        for log in state.execution_logs:
            console.print(f"  {log}")
        console.print()

    # Repo Analysis summary
    if state.repo_analysis:
        table = Table(title="Repository Analysis", show_header=True)
        table.add_column("Property", style="bold")
        table.add_column("Value")

        analysis = state.repo_analysis
        table.add_row("Languages", ", ".join(f"{l.name} ({l.percentage}%)" for l in analysis.languages))
        table.add_row("Frameworks", ", ".join(analysis.frameworks) or "None")
        table.add_row("Package Managers", ", ".join(analysis.package_managers) or "None")
        table.add_row("Docker", "Yes" if analysis.containerization.has_dockerfile else "No")
        table.add_row("Kubernetes", "Yes" if analysis.infrastructure.has_kubernetes else "No")
        table.add_row("Terraform", "Yes" if analysis.infrastructure.has_terraform else "No")
        table.add_row("Existing CI/CD", analysis.existing_ci.platform or "None")

        console.print(table)
        console.print()

    # Validation report
    if state.validation_report:
        status = "[bold green]PASSED" if state.validation_report.passed else "[bold red]FAILED"
        console.print(f"[bold]Validation:[/bold] {status}")

        if state.validation_report.issues:
            for issue in state.validation_report.issues:
                icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue.severity.value, "•")
                console.print(f"  {icon} [{issue.category}] {issue.message}")
        console.print()

    # Generated files
    if state.generated_pipeline:
        console.print(f"[bold]Generated {len(state.generated_pipeline.files)} file(s):[/bold]")

        for file in state.generated_pipeline.files:
            console.print(f"\n[bold cyan]--- {file.path} ---[/bold cyan]")
            console.print(f"[dim]{file.description}[/dim]\n")

            # Syntax highlight
            lang = "yaml" if file.path.endswith((".yml", ".yaml")) else "groovy"
            syntax = Syntax(file.content, lang, theme="monokai", line_numbers=True, word_wrap=False)
            console.print(syntax)

            # Write to disk if output_dir specified
            if output_dir:
                import os
                out_path = os.path.join(output_dir, file.path)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "w") as f:
                    f.write(file.content)
                console.print(f"  [green]Written to: {out_path}[/green]")

    # Final status
    console.print()
    if state.current_stage == "completed":
        console.print(Panel("[bold green]Pipeline generation completed successfully![/bold green]"))
    elif state.current_stage == "failed":
        console.print(Panel("[bold red]Pipeline generation failed. See logs above.[/bold red]"))


@app.command()
def validate(
    repo_url: str = typer.Argument(..., help="Repository URL to validate CI/CD for"),
) -> None:
    """Validate an existing CI/CD pipeline in a repository."""
    console.print(f"[bold]Validating CI/CD pipeline for:[/bold] {repo_url}")
    # TODO: Implement validation-only mode
    console.print("[yellow]Not yet implemented. Use 'generate --dry-run' for now.[/yellow]")


@app.command()
def version() -> None:
    """Show version information."""
    from src import __version__
    console.print(f"Agentic CI/CD Engineer v{__version__}")


if __name__ == "__main__":
    app()
