import logging
from flask import current_app
from app.models import AuditLog, db
from datetime import datetime

def setup_logging():
    pass

class ActivityLogger:
    @staticmethod
    def log_activity(user_id, action, table_name, record_id=None, changes=None):
        try:
            log = AuditLog(
                user_id=user_id,
                action=action,
                table_name=table_name,
                record_id=record_id,
                changes=str(changes) if changes else None,
                timestamp=datetime.utcnow()
            )
            db.session.add(log)
            db.session.commit()
            
            current_app.logger.info(
                f'User {user_id} performed {action} on {table_name}'
                f'{f" record {record_id}" if record_id else ""}'
            )
        except Exception as e:
            current_app.logger.error(f'Failed to log activity: {str(e)}')
            db.session.rollback()