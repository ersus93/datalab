#!/usr/bin/env python3
"""Formularios para gestión de usuarios."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp, Optional

from app.database.models import User, Cliente, UserRole
from flask_babel import lazy_gettext as _


class UserForm(FlaskForm):
    """Formulario para crear usuarios."""

    username = StringField(_('Usuario'), validators=[
        DataRequired(),
        Length(min=3, max=80)
    ])

    email = StringField(_('Email'), validators=[
        DataRequired(),
        Email()
    ])

    nombre_completo = StringField(_('Nombre Completo'), validators=[
        DataRequired(),
        Length(max=150)
    ])

    role = SelectField(_('Rol'), choices=[
        ('admin', _('Administrador')),
        ('laboratory_manager', _('Jefe de Laboratorio')),
        ('technician', _('Técnico')),
        ('client', _('Cliente')),
        ('viewer', _('Solo Lectura'))
    ], validators=[DataRequired()])

    cliente_id = SelectField(_('Cliente Asociado'), coerce=int, validators=[Optional()])

    password = PasswordField(_('Contraseña'), validators=[
        DataRequired(),
        Length(min=8, message=_('Mínimo 8 caracteres')),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
               message=_('Debe contener mayúscula, minúscula y número'))
    ])

    confirmar_password = PasswordField(_('Confirmar Contraseña'), validators=[
        DataRequired(),
        EqualTo('password', message=_('Las contraseñas no coinciden'))
    ])

    activo = BooleanField(_('Activo'), default=True)
    submit = SubmitField(_('Crear Usuario'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cliente_id.choices = [(0, _('-- Seleccionar --'))] + [
            (c.id, c.nombre) for c in Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
        ]

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(_('Este usuario ya existe'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(_('Este email ya está registrado'))

    def validate_cliente_id(self, field):
        if self.role.data == 'client' and field.data == 0:
            raise ValidationError(_('Debe seleccionar un cliente para el rol Cliente'))


class UserEditForm(FlaskForm):
    """Formulario para editar usuarios (sin cambiar username)."""

    email = StringField(_('Email'), validators=[
        DataRequired(),
        Email()
    ])

    nombre_completo = StringField(_('Nombre Completo'), validators=[
        DataRequired(),
        Length(max=150)
    ])

    role = SelectField(_('Rol'), choices=[
        ('admin', _('Administrador')),
        ('laboratory_manager', _('Jefe de Laboratorio')),
        ('technician', _('Técnico')),
        ('client', _('Cliente')),
        ('viewer', _('Solo Lectura'))
    ], validators=[DataRequired()])

    cliente_id = SelectField(_('Cliente Asociado'), coerce=int, validators=[Optional()])

    activo = BooleanField(_('Activo'), default=True)
    submit = SubmitField(_('Guardar Cambios'))

    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.cliente_id.choices = [(0, _('-- Seleccionar --'))] + [
            (c.id, c.nombre) for c in Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
        ]

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user and user.id != self.user_id:
            raise ValidationError(_('Este email ya está registrado'))

    def validate_cliente_id(self, field):
        if self.role.data == 'client' and field.data == 0:
            raise ValidationError(_('Debe seleccionar un cliente para el rol Cliente'))


class PasswordResetForm(FlaskForm):
    """Formulario para reset de contraseña por admin."""

    password = PasswordField(_('Nueva Contraseña'), validators=[
        DataRequired(),
        Length(min=8, message=_('Mínimo 8 caracteres')),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
               message=_('Debe contener mayúscula, minúscula y número'))
    ])

    confirmar_password = PasswordField(_('Confirmar Contraseña'), validators=[
        DataRequired(),
        EqualTo('password', message=_('Las contraseñas no coinciden'))
    ])

    submit = SubmitField(_('Cambiar Contraseña'))
