import pytest
from app import create_app, db
from app.models import User, Role, Fire
from datetime import datetime

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        Role.insert_roles()
        
        # Create test user
        user = User(
            username='test_user',
            email='test@example.com',
            role=Role.query.filter_by(name='User').first()
        )
        user.set_password('test123')
        db.session.add(user)
        
        # Create test admin
        admin = User(
            username='test_admin',
            email='admin@example.com',
            role=Role.query.filter_by(name='Admin').first()
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        db.session.commit()
    
    yield app
    
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    response = client.post('/auth/login', json={
        'username': 'test_admin',
        'password': 'admin123'
    })
    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}