from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth.forms import LoginForm, RegisterForm
from app.models import User, Role, Permission
from app.utils.decorators import admin_required
from app.utils.logger import ActivityLogger

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            if not user.is_active:
                flash('Аккаунт деактивирован', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            
            # Логирование входа
            ActivityLogger.log_activity(
                user_id=user.id,
                action='login',
                table_name='users',
                record_id=user.id
            )
            
            next_page = get_redirect_target()
            return redirect(next_page)
            
        flash('Неверное имя пользователя или пароль', 'error')
    return render_template('auth/login.html', form=form)

def get_redirect_target():
    if current_user.role.name == 'operator':
        return url_for('main.add_fire')
    elif current_user.role.name == 'engineer':
        return url_for('main.fires_list')
    elif current_user.role.name == 'analyst':
        return url_for('main.analytics')
    return url_for('main.index')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='user'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        ActivityLogger.log_activity(
            user_id=current_user.id,
            action='logout',
            table_name='users',
            record_id=current_user.id
        )
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/users')
@login_required
@admin_required
def users_list():
    users = User.query.all()
    return render_template('auth/users.html', users=users)

@auth.route('/user/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(id):
    user = User.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    
    ActivityLogger.log_activity(
        user_id=current_user.id,
        action='toggle_user',
        table_name='users',
        record_id=user.id,
        changes={'is_active': user.is_active}
    )
    
    status = 'активирован' if user.is_active else 'деактивирован'
    flash(f'Пользователь {user.username} {status}', 'success')
    return redirect(url_for('auth.users_list'))