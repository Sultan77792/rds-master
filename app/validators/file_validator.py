import os
from werkzeug.utils import secure_filename
from app.config import Config

class FileValidator:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate(file):
        if not file:
            return False, "Файл не выбран"
            
        if not FileValidator.allowed_file(file.filename):
            return False, "Недопустимый формат файла"
            
        if len(file.read()) > Config.MAX_CONTENT_LENGTH:
            return False, "Файл слишком большой"
            
        return True, "OK"