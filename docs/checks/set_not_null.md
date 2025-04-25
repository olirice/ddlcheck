# Set Not Null Check

**Check ID:** `set_not_null` | **Severity:** MEDIUM

## What It Checks For

This check detects `ALTER TABLE ... ALTER COLUMN ... SET NOT NULL` operations which can cause table locks and data inconsistency issues.

Example risky SQL:

```sql
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
```

## Why Its Risky

Setting a NOT NULL constraint on an existing column is risky because:

1. PostgreSQL must scan the entire table to verify no NULL values exist
2. During this scan, an ACCESS EXCLUSIVE lock is held on the table
3. For large tables, this can cause significant downtime
4. If any NULL values exist, the operation will fail, potentially leaving transactions in an unexpected state

## Safer Alternative

Instead of directly setting NOT NULL constraints, consider:

1. **Verify data first**: Ensure there are no NULL values before applying the constraint
2. **Use validation trigger**: Add a trigger to prevent new NULL values while you clean up existing ones
3. **Apply during low-traffic periods**: Schedule constraint changes during maintenance windows
4. **Use NOT VALID option**: For check constraints, consider using NOT VALID initially

Example safer approach:

```sql
-- 1. First check if there are any NULL values
SELECT COUNT(*) FROM users WHERE email IS NULL;

-- 2. Fix any NULL values
UPDATE users SET email = 'unknown@example.com' WHERE email IS NULL;

-- 3. Add a validation trigger to prevent new NULLs
CREATE TRIGGER ensure_email_not_null
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION validate_email_not_null();

-- 4. Finally, add the constraint during a maintenance window
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
```

## Configuration Options

You can configure or disable this check in your `.ddlcheck` configuration file:

```toml
# Disable this check
excluded_checks = ["set_not_null"]

# Override severity level
[severity]
set_not_null = "LOW"  # Options: HIGH, MEDIUM, LOW, INFO 