from app import create_app, db
from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health_check():
    try:
        db.session.execute('SELECT 1')
        return {'status': 'healthy'}, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {'status': 'unhealthy', 'error': str(e)}, 500

def init_database():
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {e}")

if __name__ == "__main__":
    init_database()