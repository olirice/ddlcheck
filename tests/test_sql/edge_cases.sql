-- SQL edge cases for testing parsing robustness

-- 1. Complex quoted identifiers
CREATE TABLE "user.data" (
    "column with spaces" TEXT,
    """double quoted""" INT,
    "Uppercase Column" BOOLEAN
);

-- 2. Comments with SQL keywords
-- ALTER TABLE users DROP COLUMN email;
ALTER TABLE users ADD COLUMN website TEXT; -- DROP TABLE users;

-- 3. Dollar-quoted string literals with embedded quotes
CREATE FUNCTION get_user() RETURNS TEXT AS $$
    SELECT 'User''s "name"';  -- This has both single and double quotes inside
$$ LANGUAGE SQL;

-- 4. Multiple statements on one line
DROP TABLE IF EXISTS temp_table; CREATE TABLE temp_table (id SERIAL); INSERT INTO temp_table DEFAULT VALUES;

-- 5. Statement with no trailing semicolon
UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = 1

-- 6. Empty statement (just a semicolon)
;

-- 7. Complex ALTER TABLE with multiple actions
ALTER TABLE products 
    ADD COLUMN description TEXT,
    ALTER COLUMN price TYPE NUMERIC(10,2),
    DROP COLUMN old_sku,
    RENAME COLUMN sku TO product_code;
    
-- 8. Nested subqueries
CREATE VIEW active_users AS 
SELECT * FROM users WHERE id IN (
    SELECT user_id FROM sessions WHERE last_activity > (
        SELECT CURRENT_TIMESTAMP - INTERVAL '30 days'
    )
);

-- 9. Unicode characters in identifiers
CREATE TABLE événements (
    año INT,
    beschreibung TEXT
);

-- 10. CTE (Common Table Expressions)
WITH deleted_users AS (
    DELETE FROM users WHERE last_login < '2020-01-01' RETURNING id, email
)
INSERT INTO audit_log (action, details)
SELECT 'user_deleted', json_build_object('id', id, 'email', email) FROM deleted_users; 