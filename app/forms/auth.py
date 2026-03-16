#!/usr/bin/env python3
"""Formularios de autenticación para DataLab."""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión."""

    username = StringField(
        "Usuario",
        validators=[
            DataRequired(message="El usuario es obligatorio."),
            Length(min=3, max=80, message="El usuario debe tener entre 3 y 80 caracteres."),
        ],
    )

    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="La contraseña es obligatoria.")],
    )

    remember_me = BooleanField("Recordarme")

    submit = SubmitField("Iniciar Sesión")
