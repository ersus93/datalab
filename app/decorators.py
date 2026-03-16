#!/usr/bin/env python3
"""Decoradores de control de acceso para DataLab."""

from functools import wraps
from typing import Callable

from flask import abort, flash, redirect, request, url_for
from flask_login import current_user

from app.database.models.user import UserRole


def require_role(*roles):
    """
    Decorador que requiere que el usuario tenga al menos uno de los roles especificados.

    Args:
        *roles: Roles permitidos (UserRole o string).

    Returns:
        Decorador que verifica el rol del usuario.
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debe iniciar sesión para acceder a esta página.", "warning")
                return redirect(url_for("auth.login", next=request.url))

            # Convertir strings a UserRole si es necesario
            allowed_roles = []
            for role in roles:
                if isinstance(role, str):
                    allowed_roles.append(UserRole(role))
                else:
                    allowed_roles.append(role)

            if current_user.role not in allowed_roles:
                flash("No tiene permisos para acceder a esta página.", "error")
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f: Callable) -> Callable:
    """Decorador que requiere rol de administrador."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Debe iniciar sesión para acceder a esta página.", "warning")
            return redirect(url_for("auth.login", next=request.url))

        if not current_user.is_admin():
            flash("Se requieren permisos de administrador.", "error")
            abort(403)

        return f(*args, **kwargs)

    return decorated_function


def laboratory_manager_required(f: Callable) -> Callable:
    """Decorador que requiere rol de gerente de laboratorio o superior."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Debe iniciar sesión para acceder a esta página.", "warning")
            return redirect(url_for("auth.login", next=request.url))

        if not (current_user.is_admin() or current_user.is_laboratory_manager()):
            flash("Se requieren permisos de gerente de laboratorio.", "error")
            abort(403)

        return f(*args, **kwargs)

    return decorated_function


def technician_required(f: Callable) -> Callable:
    """Decorador que requiere rol de técnico o superior."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Debe iniciar sesión para acceder a esta página.", "warning")
            return redirect(url_for("auth.login", next=request.url))

        if not (
            current_user.is_admin()
            or current_user.is_laboratory_manager()
            or current_user.is_technician()
        ):
            flash("Se requieren permisos de técnico.", "error")
            abort(403)

        return f(*args, **kwargs)

    return decorated_function


def client_access_required(client_id_param: str = "cliente_id"):
    """
    Decorador que verifica si el usuario puede acceder a datos de un cliente específico.

    Args:
        client_id_param: Nombre del parámetro que contiene el ID del cliente.

    Returns:
        Decorador que verifica el acceso al cliente.
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debe iniciar sesión para acceder a esta página.", "warning")
                return redirect(url_for("auth.login", next=request.url))

            client_id = kwargs.get(client_id_param)
            if client_id is None:
                abort(400)

            if not current_user.can_view_client_data(client_id):
                flash("No tiene permisos para ver los datos de este cliente.", "error")
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator
