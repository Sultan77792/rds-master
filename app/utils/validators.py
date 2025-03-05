from wtforms import ValidationError

class FireValidator:
    @staticmethod
    def validate(data):
        errors = []
        
        # Check required fields
        required_fields = ['region', 'location', 'area_affected', 'status']
        for field in required_fields:
            if field not in data:
                errors.append(f'Field {field} is required')
        
        # Validate area_affected
        try:
            area = float(data.get('area_affected', 0))
            if area <= 0:
                errors.append('Area affected must be greater than 0')
        except (ValueError, TypeError):
            errors.append('Area affected must be a valid number')
            
        # Validate status
        valid_statuses = ['new', 'in_progress', 'contained', 'extinguished']
        if data.get('status') not in valid_statuses:
            errors.append(f'Status must be one of: {", ".join(valid_statuses)}')
            
        return errors if errors else None