# Alter Column Type Check

**Check ID:** `alter_column_type` | **Severity:** HIGH

## What It Checks For

This check detects when column types are changed using `ALTER TABLE ... ALTER COLUMN ... TYPE`. This operation requires a table rewrite in PostgreSQL, which can cause locks and downtime for large tables.

Example risky SQL:

```sql
ALTER TABLE orders ALTER COLUMN status TYPE VARCHAR(100);
```

or statements with USING clause:

```sql
ALTER TABLE orders ALTER COLUMN amount TYPE NUMERIC(10,2) USING amount::NUMERIC(10,2);
```

## Why Its Risky

Changing a column's data type in PostgreSQL requires rewriting the entire table because:

1. PostgreSQL needs to scan every row to validate the conversion
2. This operation takes an ACCESS EXCLUSIVE lock on the table
3. For large tables, this can lead to significant downtime
4. Applications may experience timeouts or failures during the operation

## Safer Alternative

Instead of directly changing the column type, consider a multi-step approach:

1. Add a new column with the desired type
2. Update data in batches, populating the new column with converted values
3. Update application code to use both columns during transition
4. Once all data is migrated, drop the old column
5. Rename the new column to the original name (if needed)

Example:

```sql
-- Step 1: Add new column
ALTER TABLE orders ADD COLUMN status_new VARCHAR(100);

-- Step 2: Fill new column in batches (do this in application code or using a cursor)
UPDATE orders SET status_new = status::VARCHAR(100) WHERE id BETWEEN 1 AND 10000;
-- ...repeat for all batches

-- Step 3: Validation (in application code)

-- Step 4: Once validated, drop old column
ALTER TABLE orders DROP COLUMN status;

-- Step 5: Rename new column to original name
ALTER TABLE orders RENAME COLUMN status_new TO status;
```

## Configuration Options

You can configure or disable this check in your `.ddlcheck` configuration file:

```toml
# Disable this check
excluded_checks = ["alter_column_type"]

# Override severity level
[severity]
alter_column_type = "MEDIUM"  # Options: HIGH, MEDIUM, LOW, INFO
``` 