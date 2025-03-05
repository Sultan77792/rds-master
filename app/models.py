from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Boolean, Column
from datetime import datetime
from enum import Enum

class UserRole(Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'

class FireStatus(Enum):
    NEW = 'new'
    IN_PROGRESS = 'in_progress'
    CONTAINED = 'contained'
    EXTINGUISHED = 'extinguished'

class Permission:
    VIEW = 1      # Просмотр данных
    CREATE = 2    # Создание записей
    EDIT = 4      # Редактирование
    DELETE = 8    # Удаление
    EXPORT = 16   # Экспорт данных
    ADMIN = 31    # Все права

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)

    ROLES = {
        'operator': [Permission.CREATE],
        'engineer': [Permission.VIEW, Permission.CREATE, Permission.EDIT],
        'analyst': [Permission.VIEW, Permission.EXPORT],
        'admin': [Permission.ADMIN]
    }
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.VIEW],
            'Manager': [Permission.VIEW, Permission.CREATE, Permission.EDIT],
            'Admin': [Permission.VIEW, Permission.CREATE, Permission.EDIT, 
                     Permission.DELETE, Permission.ADMIN]
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = sum(roles[r])
            db.session.add(role)
        db.session.commit()

    def has_permission(self, permission):
        return self.permissions & permission == permission

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(name='User').first()

    def can(self, permission):
        return self.role is not None and \
            (self.role.permissions & permission) == permission

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def set_password(self, password):
        """Зашифровать пароль"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверить введенный пароль с хранимым хешем"""
        return check_password_hash(self.password_hash, password)

class Fire(db.Model):
    __tablename__ = 'fires'
    id = db.Column(db.Integer, primary_key=True)
    
    # Основная информация
    date_reported = db.Column(db.DateTime, nullable=False)
    region = db.Column(db.String(100), nullable=False)
    kgu_oopt = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(100))
    forestry = db.Column(db.String(100))
    quarter = db.Column(db.String(50))
    vydel = db.Column(db.String(50))
    
    # Площади
    area_total = db.Column(db.Float, nullable=False)
    area_forest = db.Column(db.Float)
    area_covered = db.Column(db.Float)
    area_top = db.Column(db.Float)
    area_non_forest = db.Column(db.Float)
    
    # Задействованные организации
    forest_guard_involved = db.Column(db.Boolean, default=False)
    forest_guard_people = db.Column(db.Integer, default=0)
    forest_guard_vehicles = db.Column(db.Integer, default=0)
    
    aps_involved = db.Column(db.Boolean, default=False)
    aps_people = db.Column(db.Integer, default=0)
    aps_vehicles = db.Column(db.Integer, default=0)
    aps_aircraft = db.Column(db.Integer, default=0)
    
    emergency_involved = db.Column(db.Boolean, default=False)
    emergency_people = db.Column(db.Integer, default=0)
    emergency_vehicles = db.Column(db.Integer, default=0)
    emergency_aircraft = db.Column(db.Integer, default=0)
    
    local_involved = db.Column(db.Boolean, default=False)
    local_people = db.Column(db.Integer, default=0)
    local_vehicles = db.Column(db.Integer, default=0)
    local_aircraft = db.Column(db.Integer, default=0)
    
    other_involved = db.Column(db.Boolean, default=False)
    other_people = db.Column(db.Integer, default=0)
    other_vehicles = db.Column(db.Integer, default=0)
    other_aircraft = db.Column(db.Integer, default=0)
    
    # Дополнительная информация
    description = db.Column(db.Text)
    damage = db.Column(db.Float)  # Ущерб в тенге
    suppression_cost = db.Column(db.Float)  # Затраты на тушение
    kpo = db.Column(db.String(100))
    attachment = db.Column(db.String(255))
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50))
    table_name = db.Column(db.String(50))
    record_id = db.Column(db.Integer)
    changes = db.Column(db.Text)
    
    user = db.relationship('User', backref='audit_logs')
    
    @property
    def formatted_changes(self):
        if self.changes:
            return json.loads(self.changes)
        return {}

    @staticmethod
    def log_change(user_id, action, table_name, record_id, changes):
        log = AuditLog(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            changes=json.dumps(changes, ensure_ascii=False)
        )
        db.session.add(log)
        db.session.commit()