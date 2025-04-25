# Drop Table Check

**Check ID:** `drop_table` | **Severity:** HIGH

## What It Checks For

This check detects `DROP TABLE` operations which could potentially cause data loss and application errors.

Example risky SQL:

```sql
DROP TABLE customers;
```

## Why Its Risky

Dropping a table is a high-risk operation because:

1. It **permanently deletes all data** stored in the table
2. It cannot be easily reversed without a proper backup
3. It can cause application errors if code still references the table
4. It may impact dependent objects like views, functions, and triggers

## Safer Alternative

Instead of immediately dropping tables, consider:

1. **Rename instead of drop**: Temporarily rename the table (e.g., add '_bak' suffix) to ensure no issues before permanently dropping it
2. **Two-step migration**: First remove all application references to the table, then drop it in a separate migration
3. **Use IF EXISTS**: Always use `DROP TABLE IF EXISTS` to prevent errors if the table doesn't exist
4. **Consider dependencies**: Check for and handle dependent objects before dropping tables

Example safer approach:

```sql
-- 1. First rename the table to mark it for deletion
ALTER TABLE customers RENAME TO customers_to_delete;

-- 2. In a later migration (after confirming no issues):
DROP TABLE IF EXISTS customers_to_delete;
```

## Configuration Options

You can configure or disable this check in your `.ddlcheck` configuration file:

```toml
# Disable this check
excluded_checks = ["drop_table"]

# Override severity level
[severity]
drop_table = "MEDIUM"  # Options: HIGH, MEDIUM, LOW, INFO
``` 