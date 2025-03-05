from flask import Blueprint, jsonify, request, current_app
from app.models import Fire, User
from app import db
from flask_login import login_required, current_user
from app.decorators import permission_required
from app.models import Permission
from app.utils.validators import FireValidator

api = Blueprint('api', __name__)

@api.route('/api/v1/fires', methods=['GET'])
@login_required
def get_fires():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Fire.query.order_by(Fire.date_reported.desc())
        
        # Filter by region if specified
        if region := request.args.get('region'):
            query = query.filter(Fire.region.ilike(f'%{region}%'))
        
        # Filter by status if specified
        if status := request.args.get('status'):
            query = query.filter(Fire.status == status)
            
        fires = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'status': 'success',
            'data': [{
                'id': fire.id,
                'region': fire.region,
                'location': fire.location,
                'status': fire.status.value,
                'area_affected': fire.area_affected,
                'date_reported': fire.date_reported.isoformat(),
                'reported_by': fire.reported_by.username
            } for fire in fires.items],
            'meta': {
                'total': fires.total,
                'pages': fires.pages,
                'current_page': fires.page,
                'per_page': per_page
            }
        })
    except Exception as e:
        current_app.logger.error(f'API Error: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api.route('/api/v1/fires', methods=['POST'])
@login_required
@permission_required(Permission.CREATE)
def create_fire():
    try:
        data = request.get_json()
        
        # Validate input data
        validator = FireValidator()
        if errors := validator.validate(data):
            return jsonify({'status': 'error', 'errors': errors}), 400
            
        fire = Fire(
            region=data['region'],
            location=data['location'],
            area_affected=float(data['area_affected']),
            status=data['status'],
            reported_by=current_user
        )
        
        db.session.add(fire)
        db.session.commit()
        
        current_app.logger.info(f'New fire created by {current_user.username}')
        
        return jsonify({
            'status': 'success',
            'message': 'Fire incident created successfully',
            'id': fire.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Create fire error: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 400