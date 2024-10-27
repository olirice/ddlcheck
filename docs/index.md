# DDLCheck

DDLCheck is a tool that scans PostgreSQL SQL migration files for potentially risky operations that could cause downtime, data loss, or other issues in production environments.

## Overview

Database migrations can be risky, especially in production environments with large tables and high traffic. DDLCheck analyzes your SQL migrations to identify operations that:

- Cause table rewrites (ALTER COLUMN TYPE, DROP COLUMN)
- Acquire excessive locks (non-CONCURRENT indexes, SET NOT NULL)
- May lead to data loss (DROP TABLE, TRUNCATE)
- Affect all rows without filtering (UPDATE without WHERE)

The goal is to help database administrators and developers make informed decisions about their migrations, avoiding unintended consequences and planning for potentially risky operations.

## Why Use DDLCheck?

- **Prevent Downtime**: Avoid operations that lock tables for extended periods
- **Prevent Data Loss**: Identify destructive operations before they run
- **Education**: Learn about PostgreSQL's behavior with different operations
- **Best Practices**: Follow community-established patterns for safer migrations

## Quick Start

```bash
# Install
pip install ddlcheck

# Check a single SQL file
ddlcheck check migration.sql

# Check a directory of SQL files
ddlcheck check migrations/

# List all available checks
ddlcheck list-checks

# Show version
ddlcheck version
```

## Example

Suppose you have a migration file `migration.sql` with the following content:

```sql
-- Add a new column with NOT NULL and DEFAULT
ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE;

-- Create an index without CONCURRENTLY
CREATE INDEX idx_users_email ON users (email);

-- Update all rows without a WHERE clause
UPDATE products SET visible = TRUE;
```

Running DDLCheck against this file:

```bash
ddlcheck check migration.sql
```

Will give you output like:

```
File: migration.sql
┏━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Line ┃ Severity ┃ Check      ┃ Message                                                                  ┃
┡━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ HIGH     │ add_column │ Column 'email_verified' added to table 'users' with NOT NULL and DEFAULT │
└──────┴──────────┴────────────┴──────────────────────────────────────────────────────────────────────────┘

Suggestion for add_column (line 1):
Consider using two separate migrations:
1. First add the column with a DEFAULT but as nullable
2. After data has been populated, add the NOT NULL constraint

... (additional output omitted) ...
```

This helps you identify potential issues before running the migration and suggests safer alternatives.

## Features

- **Multiple Check Types**: Includes checks for various risky PostgreSQL operations
- **Configurable**: Customize which checks to run and their severity
- **Helpful Suggestions**: Provides alternatives to risky operations
- **Line Numbers**: Identifies exactly where issues occur
- **Exit Codes**: Returns non-zero exit code when issues are found (useful for CI pipelines)

## Next Steps

- [Installation](installation.md)
- [Available Checks](checks/index.md)
- [Configuration](configuration.md)

## Contributing

Contributions are welcome! See the [GitHub repository](https://github.com/supabase/ddlcheck) for details on how to contribute. 