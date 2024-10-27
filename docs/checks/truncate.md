# Truncate Check

The `truncate` check detects when `TRUNCATE TABLE` statements are used. These operations can cause data loss and table locks, making them risky in production environments.

## Issue Detection

This check looks for statements like:

```sql
TRUNCATE TABLE audit_logs;
```

or

```sql
TRUNCATE audit_logs, temp_tables CASCADE;
```

## Why This Is Risky

Using `TRUNCATE TABLE` in PostgreSQL has several implications:

1. **Data Loss**: `TRUNCATE` immediately removes all rows from a table without possibility of rollback (if committed)
2. **Locking**: It acquires an ACCESS EXCLUSIVE lock on the table, blocking all concurrent access
3. **CASCADE Effects**: With CASCADE option, it can cause unexpected data loss in related tables
4. **Autovacuum**: Truncated tables don't need vacuuming, but may affect statistics/planning
5. **Transaction Visibility**: Even in a transaction, other sessions may observe the truncated state due to lock acquisition

## Recommended Approach

Instead of using `TRUNCATE`, consider these alternatives:

1. Use `DELETE FROM` with a `WHERE` clause to remove specific data:

```sql
DELETE FROM audit_logs WHERE created_at < '2023-01-01';
```

2. For large tables, use batched deletes to reduce lock time:

```sql
-- Delete in batches of 10,000 rows
DELETE FROM audit_logs 
WHERE id IN (SELECT id FROM audit_logs WHERE created_at < '2023-01-01' LIMIT 10000);
```

3. If you must clear an entire table, perform the operation during maintenance windows when application impact is minimized.

4. Consider creating a new empty table with the same structure and then renaming tables:

```sql
-- Create a new empty table with same structure
CREATE TABLE audit_logs_new (LIKE audit_logs INCLUDING ALL);

-- Switch tables
ALTER TABLE audit_logs RENAME TO audit_logs_old;
ALTER TABLE audit_logs_new RENAME TO audit_logs;

-- Later, when safe
DROP TABLE audit_logs_old;
```

## Configuration

You can configure or disable this check in your `.ddlcheck` configuration file:

```toml
# Disable this check
excluded_checks = ["truncate"]

# Override severity level
[severity]
truncate = "MEDIUM"  # Options: HIGH, MEDIUM, LOW, INFO

# Custom configuration
[truncate]
allowed_tables = ["test_data", "temp_imports"]  # Tables that are safe to truncate
```

## Related Checks

- [drop_table](drop_table.md): Similar destructive operation
- [update_without_filter](update_without_filter.md): Another operation that affects all rows 