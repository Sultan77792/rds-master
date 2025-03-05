from app import create_app, db
from app.models import User, Role
from werkzeug.security import generate_password_hash

def init_users():
    app = create_app()
    with app.app_context():
        # Операторы
        operators = {
            'operatorAkm': 'Акмолинская область',
            'oper2': 'Актюбинская область',
            'operAt': 'Атырауская область',
            # ...остальные операторы
        }
        
        # Инженеры
        engineers = {
            'eng1': 'Акмолинская область',
            'eng2': 'Актюбинская область',
            'engAt': 'Атырауская область',
            # ...остальные инженеры
        }
        
        operator_role = Role.query.filter_by(name='operator').first()
        engineer_role = Role.query.filter_by(name='engineer').first()
        
        # Создание операторов
        for username, region in operators.items():
            user = User(
                username=username,
                password_hash=generate_password_hash(username),
                role=operator_role,
                region=region
            )
            db.session.add(user)
        
        # Создание инженеров
        for username, region in engineers.items():
            user = User(
                username=username,
                password_hash=generate_password_hash(username),
                role=engineer_role,
                region=region
            )
            db.session.add(user)
        
        # Создание аналитика
        analyst_role = Role.query.filter_by(name='analyst').first()
        analyst = User(
            username='analyst',
            password_hash=generate_password_hash('qaz123'),
            role=analyst_role
        )
        db.session.add(analyst)
        
        # Создание администратора
        admin_role = Role.query.filter_by(name='admin').first()
        admin = User(
            username='admin1',
            password_hash=generate_password_hash('Qaz12345'),
            role=admin_role
        )
        db.session.add(admin)
        
        db.session.commit()