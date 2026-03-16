"""
Core Infrastructure - Configuración SQLAlchemy
Infraestructura compartida: base de datos, sesión, etc.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseORM(db.Model):
    """Clase base ORM para todos los modelos SQLAlchemy."""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creado_en = db.Column(db.DateTime, default=db.func.current_timestamp())
    modificado_en = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )
