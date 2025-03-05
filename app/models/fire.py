class Fire(db.Model):
    __table_args__ = (
        Index('idx_date_region', 'date', 'region'),
        Index('idx_area', 'area')
    )