# Drop Table Check

## Overview

The `drop_table` check detects `DROP TABLE` operations which could potentially cause data loss and application errors.

## Why This Is Important

Dropping a table is a high-risk operation because:

1. It **permanently deletes all data** stored in the table
2. It cannot be easily reversed without a proper backup
3. It can cause application errors if code still references the table
4. It may impact dependent objects like views, functions, and triggers

## Safer Approaches

Instead of immediately dropping tables, consider:

1. **Rename instead of drop**: Temporarily rename the table (e.g., add '_bak' suffix) to ensure no issues before permanently dropping it
2. **Two-step migration**: First remove all application references to the table, then drop it in a separate migration
3. **Use IF EXISTS**: Always use `DROP TABLE IF EXISTS` to prevent errors if the table doesn't exist
4. **Consider dependencies**: Check for and handle dependent objects before dropping tables

## Example

Unsafe approach (flagged by this check):

```sql
-- Immediately drop a table
DROP TABLE customers;
```

Safer approach:

```sql
-- 1. First rename the table to mark it for deletion
ALTER TABLE customers RENAME TO customers_to_delete;

-- 2. In a later migration (after confirming no issues):
DROP TABLE IF EXISTS customers_to_delete;
```

## Check Details

- **ID**: `drop_table`
- **Severity**: HIGH
- **Category**: Schema Changes 