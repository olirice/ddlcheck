# Update Without Filter Check

## Overview

The `update_without_filter` check detects `UPDATE` statements that don't include a `WHERE` clause, which could potentially update all rows in a table unintentionally.

## Why This Is Important

Running an UPDATE without a WHERE clause is extremely risky because:

1. It will modify **ALL** rows in the table
2. It can cause excessive disk I/O and CPU usage on large tables
3. It can block other operations for extended periods
4. The operation is difficult to roll back without a proper backup

## Safer Approaches

When writing UPDATE statements:

1. **Always include a WHERE clause**: Even if you intend to update all rows, make it explicit
2. **Start with a SELECT**: First run a SELECT with the same WHERE clause to verify the affected rows
3. **Use transactions**: Wrap updates in transactions so they can be rolled back if needed
4. **Limit batch size**: For large tables, update rows in smaller batches to reduce locking

## Example

Unsafe approach (flagged by this check):

```sql
-- Updates all rows in the table
UPDATE users SET active = false;
```

Safer approach:

```sql
-- Explicitly identify which rows to update
UPDATE users SET active = false WHERE last_login < '2023-01-01';

-- Or if you really want to update all rows, make it explicit
UPDATE users SET active = false WHERE 1=1; -- Intention to update all rows is clear
```

## Check Details

- **ID**: `update_without_filter`
- **Severity**: HIGH
- **Category**: Data Manipulation 