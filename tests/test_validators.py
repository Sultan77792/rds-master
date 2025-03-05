import pytest
from app.validators import FireValidator
from datetime import datetime, timedelta
from io import BytesIO

def test_date_validation():
    validator = FireValidator()
    
    # Тест даты в будущем
    future_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    errors = validator.validate({'date_reported': future_date})
    assert 'Дата не может быть в будущем' in errors
    
    # Тест даты ранее 2023
    errors = validator.validate({'date_reported': '2022-12-31'})
    assert 'Дата не может быть ранее 2023 года' in errors
    
    # Тест корректной даты
    valid_date = datetime.now().strftime('%Y-%m-%d')
    errors = validator.validate({'date_reported': valid_date})
    assert not any('Дата' in error for error in errors)

def test_area_validation():
    validator = FireValidator()
    
    # Тест отрицательной площади
    errors = validator.validate({'area_total': -1})
    assert 'Общая площадь должна быть больше 0' in errors
    
    # Тест несоответствия площадей
    data = {
        'area_total': 100,
        'area_forest': 60,
        'area_non_forest': 20
    }
    errors = validator.validate(data)
    assert 'Сумма лесной и нелесной площади должна равняться общей площади' in errors

def test_file_validation():
    validator = FireValidator()
    
    # Тест неверного формата файла
    file = BytesIO(b'test content')
    file.filename = 'test.exe'
    errors = validator.validate({}, file)
    assert 'Недопустимый формат файла' in errors
    
    # Тест превышения размера
    large_file = BytesIO(b'x' * (16 * 1024 * 1024 + 1))
    large_file.filename = 'test.pdf'
    errors = validator.validate({}, large_file)
    assert 'Размер файла превышает 16 МБ' in errors