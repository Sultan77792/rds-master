ALTER TABLE fires
    ADD CONSTRAINT fk_fires_users
    FOREIGN KEY (created_by_id) REFERENCES users(id);

ALTER TABLE audit_logs
    ADD CONSTRAINT fk_audit_users
    FOREIGN KEY (user_id) REFERENCES users(id);