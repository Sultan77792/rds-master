from app import db, create_app
from app.models import User, Role, Permission
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Создание ролей
        Role.insert_roles()
        
        # Создание администратора
        admin_role = Role.query.filter_by(name='admin').first()
        admin = User(
            username='admin1',
            email='admin@example.com',
            role=admin_role,
            password_hash=generate_password_hash('Qaz12345')
        )
        db.session.add(admin)
        
        # Создание операторов для каждого региона
        operator_role = Role.query.filter_by(name='operator').first()
        operators = {
            'operatorAkm': 'Акмолинская область',
            'oper2': 'Актюбинская область',
            # ...остальные операторы
        }
        
        for username, region in operators.items():
            operator = User(
                username=username,
                email=f'{username}@example.com',
                role=operator_role,
                region=region,
                password_hash=generate_password_hash(username)
            )
            db.session.add(operator)
        
        db.session.commit()