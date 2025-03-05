def secure_file_upload(file):
    allowed_extensions = {'pdf', 'doc', 'docx'}
    if not file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
        raise SecurityError("Недопустимый тип файла")