from datetime import datetime
from flask import current_app
import os

class FileValidator:
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB
    MIN_FILE_SIZE = 1024  # 1 KB

    @staticmethod
    def validate(file):
        errors = []
        if not file:
            return errors

        # Проверка размера
        file_size = len(file.read())
        file.seek(0)
        if file_size > FileValidator.MAX_FILE_SIZE:
            errors.append('Файл слишком большой (максимум 16 МБ)')
        elif file_size < FileValidator.MIN_FILE_SIZE:
            errors.append('Файл слишком маленький (минимум 1 КБ)')

        # Проверка формата
        if not FileValidator.allowed_file(file.filename):
            errors.append(f'Разрешены только форматы: {", ".join(FileValidator.ALLOWED_EXTENSIONS)}')

        # Проверка на вредоносное содержимое
        if FileValidator.is_potentially_dangerous(file):
            errors.append('Файл может содержать вредоносный код')

        return errors
        
        # Валидация дат
        try:
            if 'date_reported' in data:
                date = datetime.strptime(data['date_reported'], '%Y-%m-%d')
                if date > datetime.now():
                    errors.append('Дата не может быть в будущем')
                if date.year < 2023:
                    errors.append('Дата не может быть ранее 2023 года')
        except ValueError:
            errors.append('Неверный формат даты (требуется YYYY-MM-DD)')
        
        # Валидация площадей
        try:
            if 'area_total' in data:
                area_total = float(data['area_total'])
                if area_total <= 0:
                    errors.append('Общая площадь должна быть больше 0')
                
                area_forest = float(data.get('area_forest', 0))
                area_non_forest = float(data.get('area_non_forest', 0))
                
                # Проверка суммы площадей
                if abs(area_total - (area_forest + area_non_forest)) > 0.01:
                    errors.append('Сумма лесной и нелесной площади должна равняться общей площади')
                
                # Проверка лесопокрытой площади
                area_covered = float(data.get('area_covered', 0))
                if area_covered > area_forest:
                    errors.append('Лесопокрытая площадь не может превышать лесную площадь')
        except ValueError:
            errors.append('Неверный формат площади')
        
        # Валидация количества людей и техники
        for prefix in ['forest_guard', 'aps', 'emergency', 'local', 'other']:
            if f'{prefix}_involved' in data and data[f'{prefix}_involved']:
                try:
                    people = int(data.get(f'{prefix}_people', 0))
                    vehicles = int(data.get(f'{prefix}_vehicles', 0))
                    if people < 0 or vehicles < 0:
                        errors.append(f'Количество людей и техники не может быть отрицательным ({prefix})')
                except ValueError:
                    errors.append(f'Неверный формат количества людей или техники ({prefix})')
        
        # Валидация КГУ/ООПТ
        if 'kgu_oopt' in data:
            if not data['kgu_oopt']:
                errors.append('КГУ/ООПТ обязательно для заполнения')
        
        # Валидация денежных значений
        try:
            if 'damage' in data:
                damage = float(data['damage'])
                if damage < 0:
                    errors.append('Ущерб не может быть отрицательным')
            
            if 'suppression_cost' in data:
                cost = float(data['suppression_cost'])
                if cost < 0:
                    errors.append('Затраты на тушение не могут быть отрицательными')
        except ValueError:
            errors.append('Неверный формат денежных значений')
        
        # Валидация воздушных судов
        for prefix in ['aps', 'emergency', 'local', 'other']:
            if f'{prefix}_aircraft' in data:
                try:
                    aircraft = int(data[f'{prefix}_aircraft'])
                    if aircraft < 0:
                        errors.append(f'Количество воздушных судов не может быть отрицательным ({prefix})')
                except ValueError:
                    errors.append(f'Неверный формат количества воздушных судов ({prefix})')
        
        # Валидация файла приложения
        if file:
            if not FireValidator.allowed_file(file.filename):
                errors.append('Недопустимый формат файла')
            if len(file.read()) > FireValidator.MAX_FILE_SIZE:
                errors.append('Размер файла превышает 16 МБ')
            file.seek(0)  # Сброс указателя чтения файла
        
        return errors

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FireValidator.ALLOWED_EXTENSIONS

    @staticmethod
    def validate_coordinates(quarter, vydel):
        errors = []
        
        if quarter and not quarter.isdigit():
            errors.append('Квартал должен быть числом')
        
        if vydel and not vydel.isdigit():
            errors.append('Выдел должен быть числом')
        
        return errors

    @staticmethod
    def validate_organizations(data):
        errors = []
        
        # Проверка хотя бы одной задействованной организации
        organizations = ['forest_guard', 'aps', 'emergency', 'local', 'other']
        if not any(data.get(f'{org}_involved', False) for org in organizations):
            errors.append('Должна быть задействована хотя бы одна организация')
        
        return errors

class FireValidator:
    @staticmethod
    def validate_area(area):
        if area < 0:
            return "Площадь не может быть отрицательной"
        return None

    @staticmethod 
    def validate_date(date):
        if date > datetime.now():
            return "Дата не может быть в будущем"
        return None