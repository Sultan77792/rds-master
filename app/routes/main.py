@main.route('/fires')
@login_required
def fires_list():
    if current_user.role.name == 'operator':
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort = request.args.get('sort', 'date_reported')
    order = request.args.get('order', 'desc')
    search = request.args.get('search', '')

    query = Fire.query

    # Фильтрация по региону для инженеров
    if current_user.role.name == 'engineer':
        query = query.filter_by(region=current_user.region)

    # Поиск
    if search:
        query = query.filter(db.or_(
            Fire.region.ilike(f'%{search}%'),
            Fire.kgu_oopt.ilike(f'%{search}%'),
            Fire.forestry.ilike(f'%{search}%')
        ))

    # Сортировка
    if order == 'desc':
        query = query.order_by(getattr(Fire, sort).desc())
    else:
        query = query.order_by(getattr(Fire, sort).asc())

    fires = query.paginate(page=page, per_page=per_page)
    return render_template('fires/list.html', fires=fires)

@main.route('/audit-logs/export')
@login_required
@admin_required
def export_audit_logs():
    from datetime import datetime
    import pandas as pd
    
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    
    data = []
    for log in logs:
        data.append({
            'Время': log.timestamp.strftime('%d.%m.%Y %H:%M:%S'),
            'Пользователь': log.user.username,
            'Действие': log.action,
            'Таблица': log.table_name,
            'ID записи': log.record_id,
            'Изменения': log.changes
        })
    
    df = pd.DataFrame(data)
    
    # Генерация имени файла
    filename = f'audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    # Создание CSV файла
    response = make_response(df.to_csv(index=False, encoding='utf-8-sig'))
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response