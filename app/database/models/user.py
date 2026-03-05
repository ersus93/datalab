#!/usr/bin/env python3
"""Modelo de Usuario para DataLab con autenticación."""

from datetime import datetime
from enum import Enum

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class UserRole(Enum):
    """Roles de usuario del sistema."""

    ADMIN = "admin"
    LABORATORY_MANAGER = "laboratory_manager"
    TECHNICIAN = "technician"
    CLIENT = "client"
    VIEWER = "viewer"


class User(UserMixin, db.Model):
    """Modelo de Usuario con autenticación."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    nombre_completo = db.Column(db.String(200), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    # Relación con Cliente (para usuarios tipo cliente)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=True)
    cliente = db.relationship("Cliente", backref="usuarios", lazy=True)

    # Relación con preferencias de notificación
    notification_preferences = db.relationship(
        "NotificationPreference",
        back_populates="user",
        uselist=False,
        lazy=True,
        cascade="all, delete-orphan"
    )

    # Timestamps
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        """Genera hash de contraseña usando pbkdf2:sha256."""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password: str) -> bool:
        """Verifica la contraseña contra el hash almacenado."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        """Verifica si el usuario es administrador."""
        return self.role == UserRole.ADMIN

    def is_laboratory_manager(self) -> bool:
        """Verifica si el usuario es gerente de laboratorio."""
        return self.role == UserRole.LABORATORY_MANAGER

    def is_technician(self) -> bool:
        """Verifica si el usuario es técnico."""
        return self.role == UserRole.TECHNICIAN

    def is_client(self) -> bool:
        """Verifica si el usuario es cliente."""
        return self.role == UserRole.CLIENT

    def can_view_client_data(self, client_id: int) -> bool:
        """
        Verifica si el usuario puede ver datos de un cliente específico.

        Args:
            client_id: ID del cliente a verificar.

        Returns:
            bool: True si puede ver los datos, False en caso contrario.
        """
        if self.is_admin() or self.is_laboratory_manager() or self.is_technician():
            return True
        if self.is_client() and self.cliente_id == client_id:
            return True
        return False

    def to_dict(self) -> dict:
        """Convierte el usuario a diccionario (excluye datos sensibles)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "nombre_completo": self.nombre_completo,
            "role": self.role.value if self.role else None,
            "activo": self.activo,
            "cliente_id": self.cliente_id,
            "ultimo_acceso": (
                self.ultimo_acceso.isoformat() if self.ultimo_acceso else None
            ),
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "actualizado_en": (
                self.actualizado_en.isoformat() if self.actualizado_en else None
            ),
        }

    def get_notification_preferences(self):
        """Obtiene o crea las preferencias de notificación del usuario."""
        from app.database.models.notification_preference import NotificationPreference
        if not self.notification_preferences:
            return NotificationPreference.get_or_create(self.id)
        return self.notification_preferences
