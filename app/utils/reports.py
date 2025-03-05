from datetime import datetime, timedelta
from sqlalchemy import func
from app.models import Fire, FireStatus
from app import db

class ReportGenerator:
    @staticmethod
    def get_fires_by_period(start_date, end_date):
        return Fire.query.filter(
            Fire.date_reported.between(start_date, end_date)
        ).all()
    
    @staticmethod
    def get_statistics_by_region():
        return db.session.query(
            Fire.region,
            func.count(Fire.id).label('total_fires'),
            func.sum(Fire.area_affected).label('total_area')
        ).group_by(Fire.region).all()
    
    @staticmethod
    def get_status_distribution():
        return db.session.query(
            Fire.status,
            func.count(Fire.id).label('count')
        ).group_by(Fire.status).all()