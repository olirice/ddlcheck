# Configuration

DDLCheck can be configured using a TOML configuration file. By default, it looks for a file named `.ddlcheck` in the current directory, but you can specify a different file using the `--config` option.

## Configuration File Format

DDLCheck uses TOML format for configuration. Here's an example configuration file:

```toml
# List of check IDs to disable
excluded_checks = ["drop_table", "truncate"]

# Override severity levels
[severity]
create_index = "LOW"
add_column = "HIGH"

# Individual check configurations
[create_index]
ignore_non_concurrent = false
min_size_warning = 1000  # Only warn for tables likely larger than this

[update_without_filter]
allowed_tables = ["config", "settings"]  # Tables that are safe to update without filters

[truncate]
allowed_tables = ["logs_temp", "imports_staging"]  # Tables that are safe to truncate
```

## Available Configuration Options

### Global Options

| Option | Type | Description |
|--------|------|-------------|
| `excluded_checks` | List[str] | List of check IDs to disable |

### Severity Overrides

You can override the default severity level for any check by adding a section under `[severity]`:

```toml
[severity]
check_id = "SEVERITY"  # HIGH, MEDIUM, LOW, or INFO
```

### Check-Specific Options

#### CreateIndexCheck (`create_index`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `ignore_non_concurrent` | bool | `false` | Completely ignore non-concurrent indexes |
| `min_size_warning` | int | `0` | Only warn for tables likely larger than this row count (0 means all) |

#### UpdateWithoutFilterCheck (`update_without_filter`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `allowed_tables` | List[str] | `[]` | Tables that are safe to update without WHERE clauses |

#### TruncateCheck (`truncate`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `allowed_tables` | List[str] | `[]` | Tables that are safe to truncate |

## Command Line Configuration

You can also override some configuration options from the command line:

```bash
# Exclude checks by ID
ddlcheck check --exclude add_column,drop_table migration.sql

# Specify a custom config file
ddlcheck check --config my_custom_config.toml migration.sql

# Enable verbose logging
ddlcheck check --verbose migration.sql

# Write logs to a file
ddlcheck check --log-file ddlcheck.log migration.sql
```

## Configuration Precedence

Configuration options are applied in the following order (each one overrides the previous):

1. Default values
2. Configuration file
3. Command line arguments 