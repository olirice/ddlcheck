# Drop Column Check

**Check ID:** `drop_column` | **Severity:** HIGH

## What It Checks For

This check detects `ALTER TABLE ... DROP COLUMN` operations which could potentially cause data loss, application errors, and table locks.

Example risky SQL:

```sql
ALTER TABLE users DROP COLUMN email;
```

## Why Its Risky

Dropping a column is a high-risk operation because:

1. It **permanently deletes all data** stored in the column
2. It cannot be easily reversed without a proper backup
3. It can cause application errors if code still references the column
4. For PostgreSQL versions before 11, dropping a column requires a table rewrite and an ACCESS EXCLUSIVE lock
5. It may impact dependent objects like indexes, constraints, and views

## Safer Alternative

Instead of immediately dropping columns, consider:

1. **Soft deprecation**: First rename the column (e.g., add 'deprecated_' prefix) and stop using it in application code
2. **Two-phase migration**: First update all application code to stop using the column, then drop it
3. **Use transaction**: Always use transactions when dropping columns to ensure atomicity

Example safer approach:

```sql
-- 1. First rename the column to mark it as deprecated
ALTER TABLE users RENAME COLUMN email TO deprecated_email;

-- 2. In a later migration (after confirming no issues):
ALTER TABLE users DROP COLUMN deprecated_email;
```

## Configuration Options

You can configure or disable this check in your `.ddlcheck` configuration file:

```toml
# Disable this check
excluded_checks = ["drop_column"]

# Override severity level
[severity]
drop_column = "MEDIUM"  # Options: HIGH, MEDIUM, LOW, INFO
``` 