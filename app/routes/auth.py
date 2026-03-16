#!/usr/bin/env python3
"""Rutas de autenticación para DataLab."""

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from app.forms.auth import LoginForm

# Crear blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Página de inicio de sesión."""
    # Lazy import para evitar ciclos de importación
    from app.database.models.user import User

    # Si el usuario ya está autenticado, redirigir al dashboard
    from flask_login import current_user
    if request.method == "GET" and current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember_me = form.remember_me.data

        # Buscar usuario por username
        user = User.query.filter_by(username=username).first()

        # Verificar credenciales
        if user is None or not user.check_password(password):
            flash("Usuario o contraseña incorrectos.", "error")
            return render_template("auth/login.html", form=form), 401

        # Verificar si el usuario está activo
        if not user.activo:
            flash("Su cuenta ha sido desactivada. Contacte al administrador.", "error")
            return render_template("auth/login.html", form=form), 403

        # Login exitoso
        login_user(user, remember=remember_me)

        # Actualizar último acceso
        user.ultimo_acceso = datetime.utcnow()
        from app import db

        db.session.commit()

        flash(f"Bienvenido, {user.nombre_completo or user.username}!", "success")

        # Redirigir a la página solicitada o al dashboard
        next_page = request.args.get("next")
        if not next_page or not next_page.startswith("/"):
            next_page = url_for("dashboard.index")

        return redirect(next_page)

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Cierra la sesión del usuario."""
    logout_user()
    flash("Ha cerrado sesión correctamente.", "success")
    return redirect(url_for("auth.login"))
