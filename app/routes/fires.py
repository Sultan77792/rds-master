@fires.route('/add', methods=['GET', 'POST'])
@login_required
def add_fire():
    form = FireForm()
    
    # Автоматическое определение региона для оператора/инженера
    if current_user.role.name in ['operator', 'engineer']:
        form.region.data = current_user.region
        form.kgu_oopt.data = current_user.kgu_oopt
        form.region.render_kw = {'readonly': True}
        form.kgu_oopt.render_kw = {'readonly': True}
    
    if form.validate_on_submit():
        fire = Fire()
        form.populate_obj(fire)
        fire.created_by_id = current_user.id
        
        if form.attachment.data:
            filename = secure_filename(form.attachment.data.filename)
            form.attachment.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            fire.attachment = filename
        
        db.session.add(fire)
        
        try:
            db.session.commit()
            notify_new_fire(fire)  # Add this line
            ActivityLogger.log_activity(
                user_id=current_user.id,
                action='create',
                table_name='fires',
                record_id=fire.id
            )
            flash('Пожар успешно добавлен', 'success')
            return redirect(url_for('fires.list'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при добавлении пожара', 'error')
    
    return render_template('fires/form.html', form=form, title='Добавление пожара')