"""Formularios de autenticación."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from .models import User


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión."""
    username = StringField(
        'Usuario o Email',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Ingresa tu usuario o email'}
    )
    password = PasswordField(
        'Contraseña',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Ingresa tu contraseña'}
    )
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')


class RegistrationForm(FlaskForm):
    """Formulario de registro."""
    username = StringField(
        'Usuario',
        validators=[
            DataRequired(),
            Length(min=3, max=20, message='El usuario debe tener entre 3 y 20 caracteres')
        ],
        render_kw={'placeholder': 'Elige un nombre de usuario'}
    )
    email = StringField(
        'Email',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Ingresa tu email'}
    )
    first_name = StringField(
        'Nombre',
        validators=[
            DataRequired(),
            Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres')
        ],
        render_kw={'placeholder': 'Tu nombre'}
    )
    last_name = StringField(
        'Apellido',
        validators=[
            DataRequired(),
            Length(min=2, max=50, message='El apellido debe tener entre 2 y 50 caracteres')
        ],
        render_kw={'placeholder': 'Tu apellido'}
    )
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(),
            Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
        ],
        render_kw={'placeholder': 'Crea una contraseña segura'}
    )
    password2 = PasswordField(
        'Confirmar Contraseña',
        validators=[
            DataRequired(),
            EqualTo('password', message='Las contraseñas deben coincidir')
        ],
        render_kw={'placeholder': 'Confirma tu contraseña'}
    )
    submit = SubmitField('Registrarse')
    
    def validate_username(self, username):
        """Validar que el usuario no exista."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está en uso.')
    
    def validate_email(self, email):
        """Validar que el email no exista."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya está registrado.')


class ProfileForm(FlaskForm):
    """Formulario de perfil de usuario."""
    first_name = StringField(
        'Nombre',
        validators=[
            DataRequired(),
            Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres')
        ]
    )
    last_name = StringField(
        'Apellido',
        validators=[
            DataRequired(),
            Length(min=2, max=50, message='El apellido debe tener entre 2 y 50 caracteres')
        ]
    )
    email = StringField(
        'Email',
        validators=[DataRequired()]
    )
    phone = StringField(
        'Teléfono',
        validators=[Optional(), Length(max=20)],
        render_kw={'placeholder': '+1234567890'}
    )
    password = PasswordField(
        'Nueva Contraseña (opcional)',
        validators=[
            Optional(),
            Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
        ],
        render_kw={'placeholder': 'Deja en blanco para mantener la actual'}
    )
    password2 = PasswordField(
        'Confirmar Nueva Contraseña',
        validators=[
            EqualTo('password', message='Las contraseñas deben coincidir')
        ]
    )
    submit = SubmitField('Actualizar Perfil')


class ChangePasswordForm(FlaskForm):
    """Formulario para cambiar contraseña."""
    current_password = PasswordField(
        'Contraseña Actual',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Nueva Contraseña',
        validators=[
            DataRequired(),
            Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
        ]
    )
    password2 = PasswordField(
        'Confirmar Nueva Contraseña',
        validators=[
            DataRequired(),
            EqualTo('password', message='Las contraseñas deben coincidir')
        ]
    )
    submit = SubmitField('Cambiar Contraseña')