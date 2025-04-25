# Rename Column Check

## Overview

The `rename_column` check detects `ALTER TABLE ... RENAME COLUMN` operations which could potentially cause application errors if code still references the old column name.

## Why This Is Important

Renaming a column is an operation that:

1. Can cause application errors if code, views, or triggers still reference the old column name
2. Requires coordinated deployment of database changes and application changes
3. May impact reports, queries, and other database objects that aren't part of the main application code

## Safer Approaches

When renaming columns, consider:

1. **Two-phase deployment**: First update all application code to support both old and new column names, then rename the column
2. **Use views**: Create a view that exposes both the old and new column names during transition
3. **Create a new column**: Instead of renaming, add a new column, copy data, and eventually drop the old column after transition

## Example

Unsafe approach (flagged by this check):

```sql
-- Immediately rename a column
ALTER TABLE users RENAME COLUMN phone TO phone_number;
```

Safer approach:

```sql
-- 1. Keep both columns during transition 
ALTER TABLE users ADD COLUMN phone_number TEXT;
UPDATE users SET phone_number = phone;

-- 2. Create a trigger to keep data in sync
CREATE TRIGGER sync_phone_columns
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION sync_phone_columns_func();

-- 3. After application is updated, eventually drop the old column
ALTER TABLE users DROP COLUMN phone;
```

## Check Details

- **ID**: `rename_column`
- **Severity**: MEDIUM
- **Category**: Schema Changes 