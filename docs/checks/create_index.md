# Create Index Check

**Check ID:** `create_index` | **Severity:** MEDIUM

## What It Checks For

This check detects when indexes are created without the `CONCURRENTLY` option.

Example risky SQL:

```sql
CREATE INDEX idx_users_email ON users (email);
```

## Why Its Risky

When you create an index without the `CONCURRENTLY` option, PostgreSQL takes an `EXCLUSIVE` lock on the table while building the index. This lock blocks all writes to the table (such as INSERT, UPDATE, DELETE operations) until the index is fully built.

For large tables, index creation can take a long time, potentially causing:

1. Application timeouts or failures due to blocked write operations
2. Growing lock queues that affect database performance
3. Elevated latency for application queries

## Safer Alternative

Use the `CONCURRENTLY` option when creating indexes in production:

```sql
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);
```

The `CONCURRENTLY` option:

1. Uses a less restrictive lock that allows writes to continue
2. Takes longer to complete since it does multiple passes over the table
3. Cannot be used within a transaction block

Note that `CREATE INDEX CONCURRENTLY` is more expensive and slower but greatly reduces the impact on active production applications.

When using `CREATE INDEX CONCURRENTLY`:

1. You cannot use it inside a transaction block
2. If the operation fails, you may be left with an invalid index that needs to be dropped
3. It places a higher load on the database during creation

## Configuration Options

No specific configuration options for this check.
