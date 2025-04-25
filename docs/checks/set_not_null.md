# Set Not Null Check

## Overview

The `set_not_null` check detects `ALTER TABLE ... SET NOT NULL` operations which could potentially fail if existing rows contain null values.

## Why This Is Important

Adding a NOT NULL constraint to an existing column is risky because:

1. It will fail if any existing rows contain NULL values
2. It can cause long-running transactions on large tables
3. It may lead to table locks that block concurrent operations

## Safer Approaches

When adding NOT NULL constraints, consider:

1. **Validate first**: First check if there are any null values in the column
2. **Update data**: Fill in NULL values with appropriate defaults before adding the constraint
3. **Use validation trigger**: Use a trigger to prevent new NULL values while gradually fixing existing data
4. **Add with default**: When adding a new column, add it with NOT NULL and a default value in one statement

## Example

Unsafe approach (flagged by this check):

```sql
-- Directly set NOT NULL on an existing column
ALTER TABLE orders ALTER COLUMN customer_id SET NOT NULL;
```

Safer approach:

```sql
-- 1. First check if there are any null values
SELECT COUNT(*) FROM orders WHERE customer_id IS NULL;

-- 2. Update any existing NULL values
UPDATE orders SET customer_id = 0 WHERE customer_id IS NULL;

-- 3. Then add the constraint
ALTER TABLE orders ALTER COLUMN customer_id SET NOT NULL;
```

Best approach (for new columns):

```sql
-- Add a new NOT NULL column with a default in one statement
ALTER TABLE orders ADD COLUMN priority INTEGER NOT NULL DEFAULT 0;
```

## Check Details

- **ID**: `set_not_null`
- **Severity**: MEDIUM
- **Category**: Schema Changes 