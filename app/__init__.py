from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os
from app.routes.health import health_bp

app = Flask(__name__)

# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql://user:password@localhost/rds')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate()
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def create_app():
    app.config.from_object(Config)
    
    # Setup logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        file_handler = RotatingFileHandler(
            'logs/fire_incidents.log',
            maxBytes=10240,
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Fire Incidents startup')
    
    try:
        migrate.init_app(app, db)
        app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.error(f"Database initialization error: {e}")
    
    try:
        from app.auth.routes import auth
        from app.routes import main
        from app.api.routes import api
        from app.routes.export import export
        from app.routes.health import health
        from app.routes.health import health_bp
        app.register_blueprint(auth)
        app.register_blueprint(main)
        app.register_blueprint(api)
        app.register_blueprint(export)
        app.register_blueprint(health)
        app.register_blueprint(health_bp)
        app.logger.info("Routes registered successfully")
    except Exception as e:
        app.logger.error(f"Blueprint registration error: {e}")
    
    def number_filter(value):
        """Форматирование чисел с разделителями"""
        return "{:,}".format(value).replace(',', ' ')

    def currency_filter(value):
        """Форматирование денежных сумм"""
        if value is None:
            return "0"
        return "{:,.2f}".format(value).replace(',', ' ') + " ₸"

    app.jinja_env.filters['number'] = number_filter
    app.jinja_env.filters['currency'] = currency_filter

    return app

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

pandas==1.3.3
openpyxl==3.0.9