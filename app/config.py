import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://user:pass@localhost/fires_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_timeout': 20,
        'pool_size': 5
    }

    WTF_CSRF_ENABLED = False
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Export configuration
    EXPORT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'exports')
    EXPORT_FORMATS = ['csv', 'xlsx']
    EXPORT_MAX_ROWS = 1000000
    
    # Export settings
    EXPORT_PATH = os.environ.get('EXPORT_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports'))
    if not os.path.exists(EXPORT_PATH):
        os.makedirs(EXPORT_PATH)
    
    # File uploads
    UPLOAD_FOLDER = 'uploads'
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 3600
    
    # Backup settings
    BACKUP_DIR = 'backups'
    BACKUP_RETENTION_DAYS = 30