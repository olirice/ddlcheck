# Available Checks

DDLCheck includes several checks for common database schema migration issues. Each check looks for a specific pattern in your SQL that might cause problems in production.

## Check Categories

The checks are organized into the following categories:

### High Severity

These checks identify operations that can cause significant issues:

- **[add_column_not_null_default](add_column.md)**: Detects when columns are added with NOT NULL constraints and DEFAULT values
- **[alter_column_type](alter_column_type.md)**: Detects ALTER COLUMN TYPE operations that require table rewrites
- **[drop_table](drop_table.md)**: Detects DROP TABLE operations that could result in data loss
- **[truncate](truncate.md)**: Detects TRUNCATE operations which can cause data loss and locks
- **[update_without_filter](update_without_filter.md)**: Detects UPDATE statements without WHERE clauses

### Medium Severity

These checks identify operations that can cause moderate issues:

- **[create_index](create_index.md)**: Detects index creation without the CONCURRENTLY option
- **[drop_column](drop_column.md)**: Detects DROP COLUMN operations that require table rewrites
- **[rename_column](rename_column.md)**: Detects column renames that can break dependent objects
- **[set_not_null](set_not_null.md)**: Detects when NOT NULL constraints are added to existing columns

## Configuration

You can configure or disable any check in your `.ddlcheck` configuration file:

```toml
# Exclude specific checks
excluded_checks = ["truncate", "drop_table"]

# Override severity levels
[severity]
create_index = "LOW"
add_column_not_null_default = "HIGH"

# Configure individual checks
[create_index]
ignore_non_concurrent = false
min_size_warning = 1000

[update_without_filter]
allowed_tables = ["config", "settings"]
```

See the [Configuration](../configuration.md) section for more details.

## Custom Checks

You can create your own custom checks by implementing the `Check` base class. See the [Custom Checks](../custom_checks.md) section for more information.

```python
from ddlcheck.core import Check
from ddlcheck.models import Issue, SeverityLevel

class MyCustomCheck(Check):
    """A custom check implementation."""
    
    @property
    def id(self) -> str:
        return "my_custom_check"
    
    @property
    def description(self) -> str:
        return "Detects something important"
    
    @property
    def severity(self) -> SeverityLevel:
        return SeverityLevel.HIGH
    
    def check_statement(self, stmt, line):
        # Your implementation here
        return []
``` 