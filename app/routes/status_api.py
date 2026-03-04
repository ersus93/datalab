"""API endpoints para gestión de estados."""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from flask_babel import _

from app import db
from app.services.status_workflow import StatusWorkflow
from app.database.models.entrada import Entrada
from app.database.models.status_history import StatusHistory

status_api_bp = Blueprint('status_api', __name__, url_prefix='/api/status')


@status_api_bp.route('/transitions/<current_status>')
@login_required
def get_valid_transitions(current_status):
    """Obtener transiciones válidas desde un estado."""
    transitions = StatusWorkflow.get_valid_transitions(current_status)
    return jsonify({
        'current_status': current_status,
        'valid_transitions': transitions,
        'labels': {t: StatusWorkflow.STATUS_LABELS.get(t, t) for t in transitions}
    })


@status_api_bp.route('/entrada/<int:entrada_id>/change', methods=['POST'])
@login_required
def change_status(entrada_id):
    """Cambiar estado de una entrada."""
    entrada = Entrada.query.get_or_404(entrada_id)
    data = request.get_json()

    new_status = data.get('status')
    reason = data.get('reason', '')

    if not new_status:
        return jsonify({'error': _('Nuevo estado requerido')}), 400

    try:
        StatusWorkflow.transition(
            entrada=entrada,
            to_status=new_status,
            changed_by_id=current_user.id,
            reason=reason
        )
        db.session.commit()

        return jsonify({
            'success': True,
            'message': _('Estado actualizado exitosamente'),
            'entrada': entrada.to_dict()
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@status_api_bp.route('/entrada/batch-change', methods=['POST'])
@login_required
def batch_change_status():
    """Cambiar estado de múltiples entradas."""
    data = request.get_json()
    entrada_ids = data.get('entrada_ids', [])
    new_status = data.get('status')
    reason = data.get('reason', '')

    if not entrada_ids or not new_status:
        return jsonify({
            'error': _('IDs de entradas y nuevo estado requeridos')
        }), 400

    results = StatusWorkflow.batch_transition(
        entrada_ids=entrada_ids,
        to_status=new_status,
        changed_by_id=current_user.id,
        reason=reason
    )

    return jsonify({
        'success': True,
        'results': results,
        'successful': len(results['success']),
        'failed': len(results['failed'])
    })


@status_api_bp.route('/entrada/<int:entrada_id>/history')
@login_required
def get_status_history(entrada_id):
    """Obtener historial de estados de una entrada."""
    entrada = Entrada.query.get_or_404(entrada_id)
    history = entrada.status_history.all()

    return jsonify({
        'entrada_id': entrada_id,
        'history': [h.to_dict() for h in history]
    })
