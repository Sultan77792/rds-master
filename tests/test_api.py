import pytest
from app import create_app, db
from app.models import User, Fire, Role
import json

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Create test user and get auth token
    with client.application.app_context():
        db.create_all()
        Role.insert_roles()
        admin_role = Role.query.filter_by(name='Admin').first()
        user = User(username='test_admin', email='test@example.com', role=admin_role)
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()
    
    response = client.post('/auth/login', json={
        'username': 'test_admin',
        'password': 'test123'
    })
    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}

def test_get_fires(client, auth_headers):
    response = client.get('/api/v1/fires', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'data' in data

def test_create_fire(client, auth_headers):
    fire_data = {
        'region': 'Test Region',
        'location': 'Test Location',
        'area_affected': 100.0,
        'status': 'new'
    }
    response = client.post('/api/v1/fires',
                          json=fire_data,
                          headers=auth_headers)
    assert response.status_code == 201
    assert 'id' in response.json