"""Vistas de reportes."""

from flask import render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from . import reports_bp


@reports_bp.route('/')
@login_required
def index():
    """Página principal de reportes."""
    return render_template('reports/index.html')


@reports_bp.route('/create')
@login_required
def create():
    """Crear nuevo reporte."""
    return render_template('reports/create.html')


@reports_bp.route('/list')
@login_required
def list_reports():
    """Lista de reportes."""
    # Aquí se cargarían los reportes desde la base de datos
    reports = []
    return render_template('reports/list.html', reports=reports)


@reports_bp.route('/view/<int:report_id>')
@login_required
def view_report(report_id):
    """Ver reporte específico."""
    # Aquí se cargaría el reporte desde la base de datos
    return render_template('reports/view.html', report_id=report_id)


@reports_bp.route('/export/<int:report_id>/<format>')
@login_required
def export_report(report_id, format):
    """Exportar reporte en diferentes formatos."""
    if format not in ['pdf', 'excel', 'csv']:
        flash('Formato de exportación no válido.', 'danger')
        return redirect(url_for('reports.index'))
    
    # Aquí se implementaría la lógica de exportación
    flash(f'Reporte exportado en formato {format.upper()}.', 'success')
    return redirect(url_for('reports.view_report', report_id=report_id))


@reports_bp.route('/api/generate', methods=['POST'])
@login_required
def api_generate_report():
    """API endpoint para generar reportes."""
    data = request.get_json()
    
    # Validar datos de entrada
    if not data or 'type' not in data:
        return jsonify({'error': 'Tipo de reporte requerido'}), 400
    
    # Aquí se implementaría la lógica de generación
    result = {
        'success': True,
        'report_id': 1,
        'message': 'Reporte generado exitosamente'
    }
    
    return jsonify(result)