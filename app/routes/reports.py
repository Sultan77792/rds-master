@reports.route('/summary')
@login_required
@admin_or_analyst_required
def summary():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = db.session.query(
        Fire.region,
        func.count(Fire.id).label('total_fires'),
        func.sum(Fire.area_total).label('total_area'),
        func.sum(Fire.damage).label('total_damage'),
        # Общие суммы
        func.sum(
            Fire.forest_guard_people + 
            Fire.aps_people + 
            Fire.emergency_people + 
            Fire.local_people + 
            Fire.other_people
        ).label('total_people'),
        func.sum(
            Fire.forest_guard_vehicles + 
            Fire.aps_vehicles + 
            Fire.emergency_vehicles + 
            Fire.local_vehicles + 
            Fire.other_vehicles
        ).label('total_vehicles'),
        # АПС специфичные данные
        func.sum(Fire.aps_aircraft).label('aps_aircraft'),
        func.sum(Fire.aps_people).label('aps_people'),
        func.sum(Fire.aps_vehicles).label('aps_vehicles')
    ).group_by(Fire.region)
    
    if start_date:
        query = query.filter(Fire.date_reported >= start_date)
    if end_date:
        query = query.filter(Fire.date_reported <= end_date)
        
    summary = query.all()
    
    return render_template('reports/summary.html', 
                         summary=summary,
                         start_date=start_date,
                         end_date=end_date)