"""
Feature: Clientes
Capa: Infrastructure - Persistencia (Adapter SQLAlchemy)
Implementa el port ClienteRepository usando SQLAlchemy.
"""
import dataclasses
from typing import List, Optional

from app.core.infrastructure.database import BaseORM, db
from app.features.clientes.domain.models import Cliente
from app.features.clientes.domain.repositories import ClienteRepository


# ──────────────────────────────────────────────────────────────
# ORM Model (SQLAlchemy)
# ──────────────────────────────────────────────────────────────
class ClienteORM(BaseORM):
    __tablename__ = "clientes"

    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    ruc_ci = db.Column(db.String(20))
    telefono = db.Column(db.String(30))
    email = db.Column(db.String(100))
    direccion = db.Column(db.String(300))
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    muestras = db.relationship("MuestraORM", back_populates="cliente", lazy="dynamic")

    def to_domain(self) -> Cliente:
        return Cliente(
            id=self.id,
            codigo=self.codigo,
            nombre=self.nombre,
            ruc_ci=self.ruc_ci,
            telefono=self.telefono,
            email=self.email,
            direccion=self.direccion,
            activo=self.activo,
            creado_en=self.creado_en,
            modificado_en=self.modificado_en,
        )


# ──────────────────────────────────────────────────────────────
# Repository Implementation (Adapter)
# ──────────────────────────────────────────────────────────────
class SQLClienteRepository(ClienteRepository):
    """Adaptador: Repositorio de clientes con SQLAlchemy."""

    def __init__(self, session):
        self.session = session

    def get_by_id(self, entity_id: int) -> Optional[Cliente]:
        orm = self.session.get(ClienteORM, entity_id)
        return orm.to_domain() if orm else None

    def get_by_codigo(self, codigo: str) -> Optional[Cliente]:
        orm = self.session.query(ClienteORM).filter_by(codigo=codigo).first()
        return orm.to_domain() if orm else None

    def exists_by_codigo(self, codigo: str) -> bool:
        return self.session.query(
            self.session.query(ClienteORM).filter_by(codigo=codigo).exists()
        ).scalar()

    def search(self, nombre: str = "", activo: Optional[bool] = None) -> List[Cliente]:
        query = self.session.query(ClienteORM)
        if nombre:
            query = query.filter(ClienteORM.nombre.ilike(f"%{nombre}%"))
        if activo is not None:
            query = query.filter_by(activo=activo)
        return [orm.to_domain() for orm in query.order_by(ClienteORM.nombre).all()]

    def save(self, cliente: Cliente) -> Cliente:
        if cliente.id:
            orm = self.session.get(ClienteORM, cliente.id)
            if not orm:
                raise ValueError(f"Cliente {cliente.id} no encontrado en BD.")
        else:
            orm = ClienteORM()
            self.session.add(orm)

        orm.codigo = cliente.codigo
        orm.nombre = cliente.nombre
        orm.ruc_ci = cliente.ruc_ci
        orm.telefono = cliente.telefono
        orm.email = cliente.email
        orm.direccion = cliente.direccion
        orm.activo = cliente.activo

        self.session.commit()
        return orm.to_domain()

    def delete(self, entity_id: int) -> None:
        orm = self.session.get(ClienteORM, entity_id)
        if orm:
            self.session.delete(orm)
            self.session.commit()

    def list_all(self) -> List[Cliente]:
        return self.search()
