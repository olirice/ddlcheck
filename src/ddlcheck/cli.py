"""Command-line interface for DDLCheck."""

import os
import logging
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ddlcheck import __version__
from ddlcheck.checks import ALL_CHECKS
from ddlcheck.logger import setup_logging
from ddlcheck.models import CheckResult, Config, Issue, SeverityLevel

# Create the app
app = typer.Typer(help="Check SQL files for potentially dangerous operations")
console = Console()
logger = logging.getLogger(__name__)


def find_sql_files(directory: Path) -> List[Path]:
    """Find all SQL files in a directory.

    Args:
        directory: Directory to search in

    Returns:
        List of paths to SQL files
    """
    if not directory.is_dir():
        return [directory] if directory.suffix.lower() == ".sql" else []

    sql_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".sql"):
                sql_files.append(Path(root) / file)
    return sql_files


def format_severity(severity: SeverityLevel) -> Text:
    """Format severity level with color.

    Args:
        severity: Severity level to format

    Returns:
        Formatted text
    """
    if severity == SeverityLevel.HIGH:
        return Text("HIGH", style="bold red")
    elif severity == SeverityLevel.MEDIUM:
        return Text("MEDIUM", style="bold yellow")
    elif severity == SeverityLevel.LOW:
        return Text("LOW", style="bold blue")
    return Text("INFO", style="bold green")


def display_results(results: List[CheckResult]) -> None:
    """Display check results to the console.

    Args:
        results: List of check results
    """
    issue_count = sum(len(result.issues) for result in results)
    if issue_count == 0:
        console.print("[bold green]No issues found![/bold green]")
        return

    # Group issues by file
    for result in results:
        if not result.has_issues():
            continue

        # Get the file name for display
        file_path = result.file_path
        file_name = file_path.name
        
        console.print(f"\n[bold]File:[/bold] {file_path} ([bold cyan]{file_name}[/bold cyan])")

        table = Table(show_header=True, header_style="bold")
        table.add_column("Line")
        table.add_column("Severity")
        table.add_column("Check")
        table.add_column("Message")

        for issue in sorted(result.issues, key=lambda x: x.line):
            table.add_row(
                str(issue.line),
                format_severity(issue.severity),
                issue.check_id,
                issue.message,
            )

        console.print(table)

        # Show suggestions for issues
        for issue in result.issues:
            if issue.suggestion:
                console.print(
                    Panel(
                        f"[bold]{issue.message}[/bold]\n\n{issue.suggestion}",
                        title=f"Suggestion for {issue.check_id} (line {issue.line})",
                        border_style="yellow",
                    )
                )


@app.command()
def check(
    path: Path = typer.Argument(
        ...,
        help="Path to SQL file or directory of SQL files",
        exists=True,
    ),
    config_path: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file (default: .ddlcheck)",
    ),
    exclude: Optional[str] = typer.Option(
        None,
        "--exclude",
        "-e",
        help="Comma-separated list of checks to exclude",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    log_file: Optional[Path] = typer.Option(
        None,
        "--log-file",
        help="Path to log file",
    ),
):
    """Check SQL files for potentially dangerous operations."""
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level, log_file)

    logger.debug(f"Starting check with path: {path}")

    # Load config
    config = Config.from_file(config_path)

    # Add command-line excludes
    if exclude:
        excluded_checks = exclude.split(",")
        config.excluded_checks.update(excluded_checks)
        logger.debug(f"Excluding checks: {excluded_checks}")

    # Get SQL files
    sql_files = find_sql_files(path)
    if not sql_files:
        console.print(f"[bold red]No SQL files found at {path}[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"[bold]Checking {len(sql_files)} SQL files...[/bold]")
    logger.info(f"Found {len(sql_files)} SQL files to check")

    # Run checks
    results = []
    for sql_file in sql_files:
        logger.debug(f"Checking file: {sql_file}")
        for check_class in ALL_CHECKS:
            check = check_class(config)
            if check.enabled:
                logger.debug(f"Running check: {check.id}")
                results.append(check.check_file(sql_file))

    # Display results
    display_results(results)

    # Exit with error code if issues were found
    issue_count = sum(len(result.issues) for result in results)
    if issue_count > 0:
        console.print(f"[bold red]Found {issue_count} issues![/bold red]")
        logger.info(f"Found {issue_count} issues")
        raise typer.Exit(code=1)

    logger.info("Check completed successfully with no issues")


@app.command()
def list_checks():
    """List all available checks."""
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID")
    table.add_column("Description")
    table.add_column("Severity")

    for check_class in ALL_CHECKS:
        check = check_class()
        table.add_row(
            check.id,
            check.description,
            format_severity(check.severity),
        )

    console.print(table)


@app.command()
def version():
    """Show version information."""
    console.print(f"DDLCheck version {__version__}")


if __name__ == "__main__":
    app()
