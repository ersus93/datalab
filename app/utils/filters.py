"""Filtros personalizados para Jinja2."""
from datetime import datetime
from flask import Blueprint

filters_bp = Blueprint('filters', __name__)


@filters_bp.app_template_filter('timeago')
def timeago_filter(date):
    """Convertir datetime a tiempo relativo."""
    if not date:
        return ''

    now = datetime.utcnow()
    diff = now - date
    seconds = diff.total_seconds()

    if seconds < 60:
        return _('hace un momento')
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{_("hace")} {minutes} {_("minuto" if minutes == 1 else "minutos")}'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{_("hace")} {hours} {_("hora" if hours == 1 else "horas")}'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'{_("hace")} {days} {_("día" if days == 1 else "días")}'
    else:
        return date.strftime('%d/%m/%Y')


@filters_bp.app_template_filter('icon_for_destino')
def icon_for_destino(destino_sigla):
    """Retornar icono FontAwesome para destino."""
    icons = {
        'CF': 'shopping-basket',
        'AC': 'users',
        'ME': 'school',
        'CD': 'dollar-sign',
        'DE': 'star',
    }
    return icons.get(destino_sigla, 'box')
