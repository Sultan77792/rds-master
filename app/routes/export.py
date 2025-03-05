from flask import Blueprint, render_template, request, send_file
from app.services.export_service import ExportService

export = Blueprint('export', __name__)

@export.route('/export', methods=['GET'])
def export_page():
    return render_template('exports/export.html')

@export.route('/export/fires', methods=['POST'])
def export_fires():
    export_service = ExportService()
    file_path = export_service.export_fires(
        start_date=request.form.get('start_date'),
        end_date=request.form.get('end_date'),
        format=request.form.get('format', 'csv')
    )
    return send_file(
        file_path,
        as_attachment=True,
        attachment_filename=os.path.basename(file_path)
    )