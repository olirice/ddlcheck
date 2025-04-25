# Usage

DDLCheck provides a command-line interface (CLI) for checking SQL files for potentially dangerous operations.

## Basic Usage

To check a single SQL file:

```bash
ddlcheck check path/to/file.sql
```

To check all SQL files in a directory (recursively):

```bash
ddlcheck check path/to/directory
```

## Command Line Options

DDLCheck provides several command-line options to customize its behavior:

| Option               | Description                                        |
|----------------------|----------------------------------------------------|
| `--exclude`, `-e`    | Comma-separated list of checks to exclude          |
| `--config`, `-c`     | Path to configuration file (default: `.ddlcheck`)  |
| `--verbose`, `-v`    | Enable verbose output                              |
| `--log-file`         | Path to log file                                   |

### Examples

Exclude specific checks:

```bash
ddlcheck check --exclude add_column,truncate path/to/file.sql
```

Use a custom configuration file:

```bash
ddlcheck check --config my_config.toml path/to/file.sql
```

Enable verbose output:

```bash
ddlcheck check --verbose path/to/file.sql
```

## Available Commands

| Command         | Description                                |
|----------------|--------------------------------------------|
| `check`         | Check SQL files for potential issues       |
| `list-checks`   | List all available checks                  |
| `version`       | Show version information                   |

### Examples

List all available checks:

```terminal
$ ddlcheck list-checks
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ ID                 ┃ Description                                                     ┃ Severity ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ add_column         │ Detects ALTER TABLE ADD COLUMN operations                       │ HIGH     │
│ alter_column_type  │ Detects ALTER TABLE ALTER COLUMN TYPE operations                │ HIGH     │
│ create_index       │ Detects CREATE INDEX operations without CONCURRENTLY            │ MEDIUM   │
│ drop_column        │ Detects ALTER TABLE DROP COLUMN operations                      │ HIGH     │
│ drop_table         │ Detects DROP TABLE operations that could result in data loss    │ HIGH     │
│ rename_column      │ Detects ALTER TABLE RENAME COLUMN operations                    │ MEDIUM   │
│ set_not_null       │ Detects ALTER TABLE SET NOT NULL operations                     │ MEDIUM   │
│ truncate           │ Detects TRUNCATE TABLE operations                               │ HIGH     │
│ update_without_filter │ Detects UPDATE statements without a WHERE clause             │ HIGH     │
└──────────────────────┴─────────────────────────────────────────────────────────────┴──────────┘
```

Show version information:

```terminal
$ ddlcheck version
DDLCheck version 0.1.0
```

## Example Output

When checking a SQL file with issues, DDLCheck provides detailed output with highlighted issues:

```terminal
$ ddlcheck check risky_operations.sql
Checking 1 SQL files...
2025-04-24 18:53:13 - ddlcheck.cli - INFO - Found 1 SQL files to check

File: risky_operations.sql
┏━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Line ┃ Severity ┃ Check                 ┃ Message                                    ┃
┡━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ HIGH     │ update_without_filter │ UPDATE statement on table 'products'       │
│      │          │                       │ without WHERE clause                       │
└──────┴──────────┴───────────────────────┴────────────────────────────────────────────┘
╭───────────────── Suggestion for update_without_filter (line 1) ──────────────────────╮
│ UPDATE statement on table 'products' without WHERE clause                            │
│                                                                                      │
│ Add a WHERE clause to limit the rows affected by the update.                         │
│ Updating all rows in a table can cause excessive I/O and blocking.                   │
╰──────────────────────────────────────────────────────────────────────────────────────╯
Found 1 issue!
2025-04-24 18:53:13 - ddlcheck.cli - INFO - Found 1 issue
```
