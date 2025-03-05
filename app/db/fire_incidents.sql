CREATE DATABASE fire_incidents;
USE fire_incidents;
SHOW TABLES;

-- Should show these tables:
-- alembic_version
-- audit_logs
-- fires
-- user

SELECT COUNT(*) FROM fires;
SELECT COUNT(*) FROM audit_logs;
SELECT COUNT(*) FROM user;