@admin.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort = request.args.get('sort', 'timestamp')
    order = request.args.get('order', 'desc')
    search = request.args.get('search', '')

    query = AuditLog.query.join(User)

    if search:
        query = query.filter(db.or_(
            User.username.ilike(f'%{search}%'),
            AuditLog.action.ilike(f'%{search}%'),
            AuditLog.table_name.ilike(f'%{search}%')
        ))

    if order == 'desc':
        query = query.order_by(getattr(AuditLog, sort).desc())
    else:
        query = query.order_by(getattr(AuditLog, sort).asc())

    logs = query.paginate(page=page, per_page=per_page)
    return render_template('admin/audit_logs.html', logs=logs)

@admin.route('/audit-logs/export')
@login_required
@admin_required
def export_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    
    data = [{
        'Время': log.timestamp.strftime('%d.%m.%Y %H:%M:%S'),
        'Пользователь': log.user.username,
        'Действие': log.action,
        'Таблица': log.table_name,
        'ID записи': log.record_id,
        'Изменения': log.changes
    } for log in logs]
    
    df = pd.DataFrame(data)
    filename = f'audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    response = make_response(df.to_csv(index=False, encoding='utf-8-sig'))
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response