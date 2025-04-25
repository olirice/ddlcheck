# Development

This guide explains how to set up your development environment and contribute to DDLCheck.

## Setting Up

1. **Clone the repository**

```bash
git clone https://github.com/oliverrice/ddlcheck.git
cd ddlcheck
```

2. **Install Poetry**

DDLCheck uses [Poetry](https://python-poetry.org/) for dependency management. If you don't have Poetry installed:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. **Install dependencies**

```bash
poetry install
```

4. **Activate virtual environment**

```bash
poetry shell
```

## Development Tasks

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=src/ddlcheck --cov-report=term-missing
```

### Building Documentation

```bash
# Build documentation
poetry run mkdocs build

# Serve documentation locally
poetry run mkdocs serve
```

### Code Quality Tools

DDLCheck uses several tools to ensure code quality:

```bash
# Run linting
poetry run flake8

# Run type checking
poetry run mypy src

# Run all pre-commit hooks
poetry run pre-commit run --all-files
```

## Creating a New Check

To create a new check:

1. Create a new file in `src/ddlcheck/checks/my_check.py`
2. Implement the check class by extending the `Check` base class
3. Add your check to `ALL_CHECKS` in `src/ddlcheck/checks/__init__.py`
4. Add tests in `tests/checks/test_my_check.py`
5. Add documentation in `docs/checks/my_check.md`

Example of a check implementation:

```python
"""Check for something risky."""

from typing import Any, Dict, List

from ddlcheck.core import Check
from ddlcheck.models import Issue, SeverityLevel


class MyCheck(Check):
    """Check for something risky."""

    @property
    def id(self) -> str:
        """Return the unique identifier for this check."""
        return "my_check"

    @property
    def description(self) -> str:
        """Return a description of what this check looks for."""
        return "Detects something risky that could cause issues"

    @property
    def severity(self) -> SeverityLevel:
        """Return the default severity level for issues found by this check."""
        return SeverityLevel.MEDIUM

    def check_statement(self, stmt: Dict[str, Any], line: int) -> List[Issue]:
        """Check a single SQL statement for issues.

        Args:
            stmt: The parsed SQL statement
            line: The line number where the statement begins

        Returns:
            List of issues found in the statement
        """
        issues = []

        # Check logic here...
        
        if issue_detected:
            issues.append(
                self.create_issue(
                    message="Something risky was detected",
                    line=line,
                    suggestion="Here's how to fix it",
                )
            )

        return issues
```

## Release Process

1. Update version in `src/ddlcheck/__init__.py`
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. The package will be automatically published to PyPI 