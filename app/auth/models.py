"""Modelos de autenticación."""

from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from app import db


# Tabla de asociación para la relación many-to-many entre User y Role
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)


class Role(db.Model):
    """Modelo de roles de usuario."""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Role {self.name}>'


class User(UserMixin, db.Model):
    """Modelo de usuario."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Información personal
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    
    # Estado de la cuenta
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relaciones
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def full_name(self):
        """Nombre completo del usuario."""
        return f'{self.first_name} {self.last_name}'
    
    def set_password(self, password):
        """Establecer contraseña hasheada."""
        self.password_hash = generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Verificar contraseña."""
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        """Verificar si el usuario tiene un rol específico."""
        return any(role.name == role_name for role in self.roles)
    
    def add_role(self, role):
        """Agregar rol al usuario."""
        if role not in self.roles:
            self.roles.append(role)
    
    def remove_role(self, role):
        """Remover rol del usuario."""
        if role in self.roles:
            self.roles.remove(role)
    
    def update_last_login(self):
        """Actualizar timestamp del último login."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convertir usuario a diccionario."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'roles': [role.name for role in self.roles]
        }
    
    @classmethod
    def create_user(cls, username, email, password, first_name, last_name, **kwargs):
        """Crear nuevo usuario."""
        user = cls(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            **kwargs
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user