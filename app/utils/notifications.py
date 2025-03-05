from flask import current_app
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f'Failed to send email: {e}')

def send_notification(subject, recipients, body):
    msg = Message(
        subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=recipients
    )
    msg.body = body
    
    # Send email asynchronously
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()

def notify_new_fire(fire):
    admin_users = User.query.filter(User.role.has(name='Admin')).all()
    admin_emails = [user.email for user in admin_users]
    
    subject = 'Новый пожар зарегистрирован'
    body = f'''
    Зарегистрирован новый пожар:
    Регион: {fire.region}
    Местоположение: {fire.location}
    Площадь: {fire.area_affected} га
    Статус: {fire.status}
    Дата регистрации: {fire.date_reported.strftime('%d.%m.%Y %H:%M')}
    '''
    
    send_notification(subject, admin_emails, body)