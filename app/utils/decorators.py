from functools import wraps
from flask import abort
from flask_login import current_user

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_administrator():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def analyst_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.role.name == 'analyst':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def engineer_required(f):
    return permission_required(Permission.VIEW | Permission.CREATE | Permission.EDIT)(f)

def operator_required(f):
    return permission_required(Permission.CREATE)(f)