from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, TextAreaField, FileField, SubmitField, DateField,  SelectField, IntegerField,BooleanField, FloatField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError
from datetime import datetime
from regions import REGIONS_AND_LOCATIONS
def validate_date(form, field):
    if not field.data:
        raise ValidationError('This field is required.')
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Войти')
REGIONS = [
        ('Акмолинская область', 'Акмолинская область'), 
        ('Атырауская область','Атырауская область'),
        ('Алматинская область','Алматинская область'),
        ('Актюбинская область','Актюбинская область'),
        ('Восточно-Казахстанская область','Восточно-Казахстанская область'),
        ('Жамбылская область', 'Жамбылская область'),
        ('Западно-Казахстанская область','Западно-Казахстанская область'),
        ('Карагандинская область','Карагандинская область'),
        ('Костанайская область','Костанайская область'),
        ('Кызылординская область','Кызылординская область'),
        ('Мангыстауская  область','Мангыстауская  область'),
        ('Павлодарская область','Павлодарская область'),
        ('Северо-Казахстанская область','Северо-Казахстанская область'),
        ('Туркестанская область','Туркестанская область'),
        ('Область Абай','Область Абай'),
        ('Область Жетысу','Область Жетысу'),
        ('Область Улытау','Область Улытау'),
        ('г. Астана','г. Астана'),
        ('г. Алматы','г. Алматы'),
        ('г. Шымкент','г. Шымкент'), 
     
]
class FireForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(FireForm, self).__init__(*args, **kwargs)
        if current_user.role.name in ['operator', 'engineer']:
            self.region.data = current_user.region
            self.kgu_oopt.data = current_user.kgu_oopt
            self.region.render_kw = {'readonly': True}
            self.kgu_oopt.render_kw = {'readonly': True}

    # Базовая информация
    date_reported = DateField('Дата пожара', validators=[
        DataRequired(message='Укажите дату пожара'),
        lambda form, field: ValidationError('Дата не может быть в будущем')
        if field.data > datetime.now().date() else None,
        lambda form, field: ValidationError('Дата не может быть ранее 2023 года')
        if field.data.year < 2023 else None
    ])
    
    region = SelectField('Регион', choices=REGIONS, validators=[
        DataRequired(message='Выберите регион')
    ])
    
    kgu_oopt = SelectField('КГУ/ООПТ', validators=[
        DataRequired(message='Выберите КГУ/ООПТ')
    ])

    branch = StringField('Филиал')
    forestry = StringField('Лесничество')

    # Местоположение
    quarter = StringField('Квартал', validators=[
        Optional(),
        lambda form, field: ValidationError('Квартал должен быть числом')
        if field.data and not field.data.isdigit() else None
    ])
    
    vydel = StringField('Выдел', validators=[
        Optional(),
        lambda form, field: ValidationError('Выдел должен быть числом')
        if field.data and not field.data.isdigit() else None
    ])

    # Площади
    area_total = FloatField('Площадь пожара', validators=[
        DataRequired(message='Укажите общую площадь'),
        NumberRange(min=0.01, message='Площадь должна быть больше 0')
    ])
    
    area_forest = FloatField('Площадь лесная', validators=[
        Optional(),
        NumberRange(min=0, message='Площадь не может быть отрицательной')
    ])
    
    area_covered = FloatField('Площадь лесная лесопокрытая', validators=[Optional()])
    area_top = FloatField('Площадь верховой', validators=[Optional()])
    area_non_forest = FloatField('Площадь не лесная', validators=[Optional()])

    def validate_area_covered(self, field):
        if field.data and self.area_forest.data:
            if field.data > self.area_forest.data:
                raise ValidationError('Лесопокрытая площадь не может превышать лесную площадь')

    def validate_area_total(self, field):
        forest = self.area_forest.data or 0
        non_forest = self.area_non_forest.data or 0
        if abs(field.data - (forest + non_forest)) > 0.01:
            raise ValidationError('Сумма лесной и нелесной площади должна равняться общей площади')

    # Службы
    forest_guard_involved = BooleanField('Лесная охрана задействована')
    forest_guard_people = IntegerField('Кол-во людей Лесной охраны', validators=[
        Optional(),
        NumberRange(min=0, message='Количество людей не может быть отрицательным')
    ])
    forest_guard_vehicles = IntegerField('Кол-во техники Лесной охраны', validators=[
        Optional(),
        NumberRange(min=0, message='Количество техники не может быть отрицательным')
    ])

    def validate_forest_guard_people(self, field):
        if self.forest_guard_involved.data and not field.data:
            raise ValidationError('Укажите количество людей Лесной охраны')

    # Файл
    attachment = FileField('Приложение', validators=[
        Optional(),
        lambda form, field: ValidationError('Размер файла превышает 16 МБ')
        if field.data and len(field.data.read()) > 16 * 1024 * 1024 else None
    ])

    def validate_attachment(self, field):
        if field.data:
            field.data.seek(0)  # Сброс указателя чтения
            filename = field.data.filename.lower()
            if not ('.' in filename and filename.rsplit('.', 1)[1] in 
                   {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}):
                raise ValidationError('Недопустимый формат файла')

    def validate(self):
        if not super().validate():
            return False
        
        # Проверка хотя бы одной задействованной организации
        if not any([
            self.forest_guard_involved.data,
            self.aps_involved.data,
            self.emergency_involved.data,
            self.local_involved.data,
            self.other_involved.data
        ]):
            self.forest_guard_involved.errors = ['Должна быть задействована хотя бы одна организация']
            return False
        
        return True

class ExportForm(FlaskForm):
    start_date = DateField('Start Date', format='%Y-%m-%d')
    end_date = DateField('End Date', format='%Y-%m-%d')
    submit = SubmitField('Export')

class ReportForm(FlaskForm):
    start_date = DateField('Начальная дата', validators=[DataRequired()])
    end_date = DateField('Конечная дата', validators=[DataRequired()])
    report_type = SelectField('Тип отчета', choices=[
        ('summary', 'Сводный отчет'),
        ('by_region', 'По регионам'),
        ('by_status', 'По статусам')
    ])

class FireValidation:
    pass
