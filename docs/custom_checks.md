# Creating Custom Checks

DDLCheck can be extended with custom checks to fit your organization's specific needs and database practices.

## Custom Check Basics

A check in DDLCheck is a Python class that:

1. Extends the `Check` base class
2. Implements required properties (`id`, `description`, `severity`)
3. Implements the `check_statement` method to analyze SQL statements

## Creating a Custom Check

### 1. Create a New Python File

Create a new file for your custom check, either:
- Inside the DDLCheck package (if contributing to the project)
- In your own package or script (if extending for your specific use case)

### 2. Implement the Check Class

Here's a template for a custom check:

```python
"""Custom check for something specific to your organization."""

from typing import Any, Dict, List

from ddlcheck.core import Check
from ddlcheck.models import Issue, SeverityLevel


class MyCustomCheck(Check):
    """Check for something specific to your organization."""

    @property
    def id(self) -> str:
        """Return the unique identifier for this check."""
        return "my_custom_check"

    @property
    def description(self) -> str:
        """Return a description of what this check looks for."""
        return "Detects something specific to your organization"

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

        # Implement your custom check logic here
        # Example: Check if a statement contains a specific table

        # if "some_condition":
        #     issues.append(
        #         self.create_issue(
        #             message="Message describing the issue",
        #             line=line,
        #             suggestion="Suggestion for how to fix it",
        #         )
        #     )

        return issues
```

### 3. Register Your Custom Check

To use your custom check with DDLCheck, you need to register it in one of the following ways:

#### Option 1: Extend the checks module

If you're contributing to DDLCheck itself, add your check to the `ALL_CHECKS` list in `src/ddlcheck/checks/__init__.py`:

```python
from ddlcheck.checks.my_custom_check import MyCustomCheck

# List of all available checks
ALL_CHECKS = [
    # ... existing checks ...
    MyCustomCheck,
]
```

#### Option 2: Use a plugin system (future feature)

In the future, DDLCheck may support a plugin system to load custom checks without modifying the core code.

#### Option 3: Create a custom entry point

You can create your own script that imports DDLCheck and registers your custom checks:

```python
#!/usr/bin/env python

from ddlcheck.cli import app
from ddlcheck.checks import ALL_CHECKS
from my_module.my_custom_check import MyCustomCheck

# Add your custom check
ALL_CHECKS.append(MyCustomCheck)

if __name__ == "__main__":
    app()
```

## SQL Statement Structure

The `stmt` parameter passed to `check_statement` is a dictionary representation of the parsed SQL AST (Abstract Syntax Tree) using the [pglast](https://github.com/lelit/pglast) library.

The structure varies based on the statement type:

* The key is the statement type (e.g., `"SelectStmt"`, `"AlterTableStmt"`, `"CreateIndexStmt"`)
* The value is the parsed statement object with properties specific to that statement type

To understand the statement structure for your custom check, it can be helpful to:

1. Use print debugging: `print(stmt)` to see the full structure
2. Check existing checks for similar SQL statements
3. Refer to the [PostgreSQL parser source code](https://github.com/postgres/postgres/blob/master/src/include/nodes/parsenodes.h) for detailed node definitions
