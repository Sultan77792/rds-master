import pytest
from app import create_app, db
from app.models import User, Role, Fire

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        Role.insert_roles()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_operator_permissions(client):
    # Создаем оператора
    operator_role = Role.query.filter_by(name='operator').first()
    operator = User(username='test_operator', 
                   email='operator@test.com',
                   role=operator_role,
                   region='Акмолинская область')
    operator.set_password('test123')
    db.session.add(operator)
    db.session.commit()
    
    # Логинимся
    client.post('/auth/login', data={
        'username': 'test_operator',
        'password': 'test123'
    })
    
    # Проверяем доступ к страницам
    assert client.get('/fires').status_code == 403  # Нет доступа к списку
    assert client.get('/fires/add').status_code == 200  # Есть доступ к добавлению
    assert client.get('/fires/1/edit').status_code == 403  # Нет доступа к редактированию