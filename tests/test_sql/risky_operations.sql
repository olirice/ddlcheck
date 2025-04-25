-- Examples of risky PostgreSQL operations that DDLCheck should detect

-- Adding a column with NOT NULL and DEFAULT (risky - locks table)
ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE;

-- Non-concurrent index creation (risky - locks table)
CREATE INDEX idx_users_email ON users (email);

-- Update without a WHERE clause (risky - affects all rows)
UPDATE products SET visible = TRUE;

-- Alter column type (risky - rewrites table)
ALTER TABLE orders ALTER COLUMN status TYPE VARCHAR(100);

-- Drop column (risky - requires table rewrite)
ALTER TABLE customers DROP COLUMN old_address;

-- Rename column (risky - breaks dependent objects)
ALTER TABLE products RENAME COLUMN name TO product_name;

-- Set NOT NULL constraint (risky - scans entire table)
ALTER TABLE orders ALTER COLUMN customer_id SET NOT NULL;

-- Drop table (risky - data loss)
DROP TABLE old_logs;

-- Truncate table (risky - data loss)
TRUNCATE TABLE audit_history;
