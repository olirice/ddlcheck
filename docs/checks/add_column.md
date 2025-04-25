# Add Column Check

**Check ID:** `add_column_not_null_default` | **Severity:** HIGH

## What It Checks For

This check detects when columns are added with both a `NOT NULL` constraint and a `DEFAULT` value in the same statement.

Example risky SQL:

```sql
ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE;
```

## Why Its Risky

When you add a column with both `NOT NULL` and `DEFAULT` constraints, PostgreSQL has to perform the following operations:

1. Take an ACCESS EXCLUSIVE lock on the table (blocks all queries)
2. Add the column to the table metadata
3. Update every row in the table to set the default value
4. Add the NOT NULL constraint

For large tables, this can cause significant downtime because the table is locked for the entire operation. The larger the table, the longer the lock is held.

## Safer Alternative

Split this operation into two separate migrations:

First migration:

```sql
-- Add the column as nullable with a default value
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
```

Second migration (after the first has been applied and data is populated):

```sql
-- Set the NOT NULL constraint separately
ALTER TABLE users ALTER COLUMN email_verified SET NOT NULL;
```

This approach:

1. Adds the column with a default value which is a metadata-only operation
2. Allows new rows to be inserted with the default value
3. Sets the NOT NULL constraint separately, which still requires a full table scan but is a separate operation

## Configuration Options

None specific to this check.
