@main.route('/fires')
@login_required
def fires_list():
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
            Fire.kgu_oopt.ilike(f'%{search}%')
        ))

    # Сортировка
    if order == 'desc':
        query = query.order_by(getattr(Fire, sort).desc())
    else:
        query = query.order_by(getattr(Fire, sort).asc())

    fires = query.paginate(page=page, per_page=per_page)
    return render_template('fires/list.html', fires=fires)