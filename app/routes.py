from flask import Blueprint, render_template, jsonify, flash, redirect, url_for, current_app, request, send_from_directory, abort
from flask_login import login_required, current_user
from .models import User, Fire, AuditLog, FireStatus, Permission
from . import db
from .forms import FireForm
from app.utils.reports import ReportGenerator
from .decorators import permission_required, admin_required
from app.utils.export import DataExporter
from app.utils.notifications import notify_new_fire

main = Blueprint('main', __name__)

@main.route('/')
def index():
    try:
        fire_count = Fire.query.count()
        user_count = User.query.count()
        audit_count = AuditLog.query.count()
        
        return render_template('index.html',
                             fire_count=fire_count,
                             user_count=user_count,
                             audit_count=audit_count)
    except Exception as e:
        current_app.logger.error(f"Error in index route: {e}")
        return render_template('error.html', error=str(e)), 500

@main.route('/fires')
@login_required
def fires_list():
    if current_user.role.name == 'operator':
        abort(403)
        
    query = Fire.query
    
    if current_user.role.name == 'engineer':
        query = query.filter_by(region=current_user.region)
    elif current_user.role.name == 'analyst':
        query = query  # Только просмотр
    elif not current_user.is_administrator:
        abort(403)
        
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort = request.args.get('sort', 'date_reported')
    order = request.args.get('order', 'desc')
    search = request.args.get('search', '')

    # Поиск
    if search:
        query = query.filter(db.or_(
            Fire.region.ilike(f'%{search}%'),
            Fire.kgu_oopt.ilike(f'%{search}%')
        ))

    # Сортировка
    if order == 'desc':
        query = query.order_by(getattr(Fire, sort).desc())
    else:
        query = query.order_by(getattr(Fire, sort).asc())

    fires = query.paginate(page=page, per_page=per_page)
    return render_template('fires/list.html', fires=fires)

@main.route('/fires/add', methods=['GET', 'POST'])
@login_required
def add_fire():
    if request.method == 'POST':
        # Получаем данные формы
        data = request.form.to_dict()
        file = request.files.get('attachment')
        
        # Валидация данных
        validator = FireValidator()
        errors = validator.validate(data, file)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('fires/add.html', form=data)
        
        try:
            # Создание записи о пожаре
            fire = Fire()
            for key, value in data.items():
                if hasattr(fire, key):
                    setattr(fire, key, value)
            
            # Сохранение файла если есть
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                fire.attachment = filename
            
            db.session.add(fire)
            db.session.commit()
            notify_new_fire(fire)  # Add this line
            
            flash('Пожар успешно добавлен', 'success')
            return redirect(url_for('main.fires_list'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error adding fire: {str(e)}')
            flash('Ошибка при добавлении пожара', 'error')
            return render_template('fires/add.html', form=data)
    
    return render_template('fires/add.html')

@main.route('/fires/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.EDIT)
def edit_fire(id):
    fire = Fire.query.get_or_404(id)
    form = FireForm(obj=fire)
    if form.validate_on_submit():
        fire.region = form.region.data
        fire.location = form.location.data
        fire.area_affected = form.area_affected.data
        fire.status = form.status.data
        fire.description = form.description.data
        db.session.commit()
        flash('Пожар успешно обновлен.', 'success')
        return redirect(url_for('main.fires_list'))
    return render_template('fires/edit.html', form=form, fire=fire)

@main.route('/fires/<int:id>/delete', methods=['POST'])
@login_required
@permission_required(Permission.DELETE)
def delete_fire(id):
    fire = Fire.query.get_or_404(id)
    db.session.delete(fire)
    db.session.commit()
    flash('Пожар успешно удален.', 'success')
    return redirect(url_for('main.fires_list'))

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/health')
def health():
    try:
        db.session.execute('SELECT 1')
        return jsonify({"status": "healthy"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@main.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    form = ReportForm()
    data = None
    
    if form.validate_on_submit():
        generator = ReportGenerator()
        
        if form.report_type.data == 'summary':
            data = generator.get_fires_by_period(
                form.start_date.data,
                form.end_date.data
            )
        elif form.report_type.data == 'by_region':
            data = generator.get_statistics_by_region()
        elif form.report_type.data == 'by_status':
            data = generator.get_status_distribution()
            
    return render_template('reports/index.html', form=form, data=data)

@main.route('/statistics')
@login_required
def statistics():
    # Отсутствует статистика
    pass

@main.route('/admin')
@login_required
@admin_required
def admin():
    return render_template('admin/index.html')

@main.route('/fires/export/excel')
@login_required
@permission_required(Permission.VIEW)
def export_fires_excel():
    fires = Fire.query.all()
    filename = DataExporter.to_excel(fires)
    return send_from_directory(
        directory=os.path.join(current_app.root_path, 'static', 'exports'),
        path=filename,
        as_attachment=True
    )

@main.route('/fires/export', methods=['GET'])
@login_required
def export_fires():
    try:
        fires = Fire.query.all()
        filename = DataExporter.to_excel(fires)
        return send_from_directory(
            current_app.config['EXPORT_PATH'],
            filename,
            as_attachment=True
        )
    except Exception as e:
        current_app.logger.error(f'Export error: {str(e)}')
        flash('Ошибка при экспорте данных', 'error')
        return redirect(url_for('main.fires_list'))

@main.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'timestamp')
    order = request.args.get('order', 'desc')

    query = AuditLog.query

    if search:
        query = query.join(User).filter(db.or_(
            User.username.ilike(f'%{search}%'),
            AuditLog.action.ilike(f'%{search}%'),
            AuditLog.table_name.ilike(f'%{search}%')
        ))

    if order == 'desc':
        query = query.order_by(db.desc(getattr(AuditLog, sort)))
    else:
        query = query.order_by(db.asc(getattr(AuditLog, sort)))

    logs = query.paginate(page=page, per_page=per_page)
    return render_template('audit/logs.html', logs=logs)

@main.route('/summary')
@login_required
@admin_or_analyst_required
def summary():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = db.session.query(
        Fire.region,
        func.count(Fire.id).label('total_fires'),
        func.sum(Fire.area_total).label('total_area'),
        func.sum(Fire.area_forest).label('forest_area'),
        func.sum(Fire.area_covered).label('covered_area'),
        func.sum(Fire.area_top).label('top_area'),
        func.sum(Fire.area_non_forest).label('non_forest_area'),
        func.sum(Fire.damage).label('total_damage'),
        # Общий персонал
        func.sum(
            Fire.forest_guard_people + 
            Fire.aps_people + 
            Fire.emergency_people + 
            Fire.local_people + 
            Fire.other_people
        ).label('total_people'),
        # Общая техника
        func.sum(
            Fire.forest_guard_vehicles + 
            Fire.aps_vehicles + 
            Fire.emergency_vehicles + 
            Fire.local_vehicles + 
            Fire.other_vehicles
        ).label('total_vehicles'),
        # Воздушные суда
        func.sum(
            Fire.aps_aircraft + 
            Fire.emergency_aircraft + 
            Fire.local_aircraft + 
            Fire.other_aircraft
        ).label('total_aircraft'),
        # АПС данные
        func.sum(Fire.aps_aircraft).label('aps_aircraft'),
        func.sum(Fire.aps_people).label('aps_people'),
        func.sum(Fire.aps_vehicles).label('aps_vehicles')
    ).group_by(Fire.region)
    
    if start_date:
        query = query.filter(Fire.date_reported >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Fire.date_reported <= datetime.strptime(end_date, '%Y-%m-%d'))
        
    summary = query.all()
    
    # Расчет итогов
    totals = {
        'total_fires': sum(r.total_fires for r in summary),
        'total_area': sum(r.total_area for r in summary),
        'total_damage': sum(r.total_damage for r in summary),
        'total_people': sum(r.total_people for r in summary),
        'total_vehicles': sum(r.total_vehicles for r in summary),
        'total_aircraft': sum(r.total_aircraft for r in summary),
        'aps_aircraft': sum(r.aps_aircraft for r in summary),
        'aps_people': sum(r.aps_people for r in summary),
        'aps_vehicles': sum(r.aps_vehicles for r in summary)
    }
    
    return render_template('summary.html', 
                         summary=summary,
                         totals=totals,
                         start_date=start_date,
                         end_date=end_date)

@main.route('/export')
@login_required
@admin_or_analyst_required
def export_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Fire.query
    
    if start_date:
        query = query.filter(Fire.date_reported >= start_date)
    if end_date:
        query = query.filter(Fire.date_reported <= end_date)