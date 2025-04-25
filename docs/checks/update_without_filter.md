# Update Without Filter Check

**Check ID:** `update_without_filter` | **Severity:** HIGH

## What It Checks For

This check detects `UPDATE` statements that don't include a `WHERE` clause, which would update all rows in a table.

Example risky SQL:

```sql
UPDATE products SET price = price * 1.1;
```

## Why Its Risky

Executing an UPDATE without a WHERE clause is risky because:

1. It affects **all rows** in the table, which is rarely the intended behavior
2. It can cause excessive I/O and blocking on large tables
3. It may lead to unintended data changes that are difficult to reverse
4. It can significantly impact application performance during execution

## Safer Alternative

Always include a WHERE clause in UPDATE statements to limit the scope of changes:

```sql
-- Update specific products only
UPDATE products SET price = price * 1.1 WHERE category = 'electronics';
```

If you genuinely need to update all rows, consider:

1. Adding an explicit condition that makes the intention clear:

```sql
-- Makes it clear all rows are intentionally being updated
UPDATE products SET last_inventory_check = CURRENT_TIMESTAMP 
WHERE TRUE;
```

2. For large tables, use batched updates to reduce lock time:

```sql
-- Update in smaller batches
UPDATE products SET price = price * 1.1 
WHERE id BETWEEN 1 AND 10000;
```

## Configuration Options

You can configure or disable this check in your `.ddlcheck` configuration file:

```toml
# Disable this check
excluded_checks = ["update_without_filter"]

# Override severity level
[severity]
update_without_filter = "MEDIUM"  # Options: HIGH, MEDIUM, LOW, INFO

# Custom configuration
[update_without_filter]
allowed_tables = ["one_row_settings"]  # Tables that are safe to update without WHERE
``` 