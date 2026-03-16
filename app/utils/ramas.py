"""Utilidades para sectores (ramas)."""

RAMA_COLORS = {
    1: {'name': 'Carne', 'color': '#dc3545', 'badge': 'danger'},
    2: {'name': 'Lácteos', 'color': '#007bff', 'badge': 'primary'},
    3: {'name': 'Vegetales', 'color': '#28a745', 'badge': 'success'},
    4: {'name': 'Bebidas', 'color': '#6f42c1', 'badge': 'purple'},
    5: {'name': 'Confitería', 'color': '#e83e8c', 'badge': 'pink'},
    6: {'name': 'Pescado', 'color': '#17a2b8', 'badge': 'info'},
    7: {'name': 'Cereales', 'color': '#ffc107', 'badge': 'warning'},
    8: {'name': 'Grasas', 'color': '#fd7e14', 'badge': 'orange'},
    9: {'name': 'Especies', 'color': '#20c997', 'badge': 'teal'},
    10: {'name': 'Conservas', 'color': '#6610f2', 'badge': 'indigo'},
    11: {'name': 'Panadería', 'color': '#795548', 'badge': 'brown'},
    12: {'name': 'Otros alimentos', 'color': '#6c757d', 'badge': 'secondary'},
    13: {'name': 'No alimentos', 'color': '#343a40', 'badge': 'dark'},
}

DESTINO_ICONS = {
    'CF': 'shopping-basket',
    'AC': 'users',
    'ME': 'school',
    'CD': 'dollar-sign',
    'DE': 'star',
}


def get_rama_color(rama_id):
    """Obtener información de color para una rama."""
    return RAMA_COLORS.get(rama_id, {'color': '#6c757d', 'badge': 'secondary'})


def get_destino_icon(destino_sigla):
    """Obtener icono para un destino."""
    return DESTINO_ICONS.get(destino_sigla, 'box')
