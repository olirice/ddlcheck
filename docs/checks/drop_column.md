# Drop Column Check

## Overview

The `drop_column` check detects `ALTER TABLE ... DROP COLUMN` operations which could potentially cause application errors if code still references the removed column.

## Why This Is Important

Dropping a column is a destructive operation that:

1. Permanently removes all data stored in that column
2. Can cause application errors if code or views still reference the removed column
3. Cannot be easily rolled back in case of issues

## Safer Approaches

Instead of immediately dropping columns, consider:

1. **Two-step migration**: First remove all application references to the column, then drop it in a separate migration after confirming no issues
2. **Comment in code**: Add a comment in the migration indicating that application code changes should be deployed first
3. **Rename instead of drop**: Temporarily rename the column (e.g., add '_to_delete' suffix) to ensure no issues before permanently dropping it

## Example

Unsafe approach (flagged by this check):

```sql
-- Immediately drop a column
ALTER TABLE users DROP COLUMN phone_number;
```

Safer approach:

```sql
-- 1. First migration: Rename the column to mark it for deletion
-- Deploy application changes that stop using this column
ALTER TABLE users RENAME COLUMN phone_number TO phone_number_to_delete;

-- 2. Second migration (later, after confirming no issues):
ALTER TABLE users DROP COLUMN phone_number_to_delete;
```

## Check Details

- **ID**: `drop_column`
- **Severity**: HIGH
- **Category**: Schema Changes 