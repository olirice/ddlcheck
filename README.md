# DDLCheck

[![PyPI version](https://img.shields.io/pypi/v/ddlcheck)](https://pypi.org/project/ddlcheck/)
[![CI](https://github.com/olirice/ddlcheck/actions/workflows/ci.yml/badge.svg)](https://github.com/olirice/ddlcheck/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/olirice/ddlcheck/badge.svg?branch=main)](https://coveralls.io/github/olirice/ddlcheck?branch=main)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

DDLCheck is a tool that scans PostgreSQL SQL migration files for potentially risky operations that could cause downtime, data loss, or other issues in production environments.

## Overview

Database migrations can be risky, especially in production environments with large tables and high traffic. DDLCheck analyzes your SQL migrations to identify operations that:

- Cause table rewrites (ALTER COLUMN TYPE, DROP COLUMN)
- Acquire excessive locks (non-CONCURRENT indexes, SET NOT NULL)
- May lead to data loss (DROP TABLE, TRUNCATE)
- Affect all rows without filtering (UPDATE without WHERE)

## Installation

```bash
# Install with pip
pip install ddlcheck

# Or with Poetry
poetry add ddlcheck
```

## Usage

```bash
# Check a single SQL file
ddlcheck check migration.sql

# Check a directory of SQL files
ddlcheck check migrations/

# Exclude specific checks
ddlcheck check migrations/ --exclude add_column_not_null_default,drop_table

# List all available checks
ddlcheck list-checks

# Show version
ddlcheck version
```

## Example Output

```
File: migration.sql
┏━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Line ┃ Severity ┃ Check      ┃ Message                                                                  ┃
┡━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ HIGH     │ add_column_not_null_default │ Column 'email_verified' added to table 'users' with NOT NULL and DEFAULT │
└──────┴──────────┴────────────┴──────────────────────────────────────────────────────────────────────────┘

Suggestion for add_column_not_null_default (line 1):
Consider using two separate migrations:
1. First add the column with a DEFAULT but as nullable
2. After data has been populated, add the NOT NULL constraint
```

## Available Checks

DDLCheck includes multiple checks for common risky operations:

- **High Severity**:
  - `add_column_not_null_default`: Detects when columns are added with NOT NULL constraints and DEFAULT values
  - `alter_column_type`: Detects ALTER COLUMN TYPE operations that require table rewrites
  - `drop_table`: Detects DROP TABLE operations that could result in data loss
  - `truncate`: Detects TRUNCATE operations which can cause data loss and locks
  - `update_without_filter`: Detects UPDATE statements without WHERE clauses

- **Medium Severity**:
  - `create_index`: Detects index creation without the CONCURRENTLY option
  - `drop_column`: Detects DROP COLUMN operations that require table rewrites
  - `rename_column`: Detects column renames that can break dependent objects
  - `set_not_null`: Detects when NOT NULL constraints are added to existing columns

## Configuration

You can configure DDLCheck using a `.ddlcheck` file in TOML format:

```toml
# List of check IDs to disable
excluded_checks = ["drop_table", "truncate"]

# Override severity levels
[severity]
create_index = "LOW"
add_column_not_null_default = "HIGH"

# Individual check configurations
[create_index]
ignore_non_concurrent = false
min_size_warning = 1000
```

## Documentation

For more detailed documentation, please visit our [documentation site](https://olirice.github.io/ddlcheck).

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for more information on how to get started.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
