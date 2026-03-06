"""
Feature: Clientes
Capa: Infrastructure > Persistence
Adaptador SQL del repositorio de clientes (implementación del puerto).

NOTA: Archivo recreado en auditoría 2026-03-05.
El archivo fuente fue eliminado accidentalmente (solo existía el .pyc).
"""
from typing import List, Optional

from app.core.infrastructure.database import db
from app.database.models.cliente import Cliente as ClienteModel
from app.features.clientes.domain.models import Cliente
from app.features.clientes.domain.repositories import ClienteRepository


def _model_to_domain(m: ClienteModel) -> Cliente:
    """Convierte un modelo SQLAlchemy a entidad de dominio."""
    return Cliente(
        id=m.id,
        codigo=m.codigo,
        nombre=m.nombre,
        email=m.email,
        telefono=m.telefono,
        direccion=m.direccion,
        activo=m.activo,
        organismo_id=m.organismo_id,
        tipo_cliente=m.tipo_cliente,
    )


class SQLClienteRepository(ClienteRepository):
    """Implementación SQL del repositorio de clientes usando SQLAlchemy."""

    def get(self, id: int) -> Optional[Cliente]:
        """Obtener cliente por ID."""
        model = ClienteModel.query.get(id)
        return _model_to_domain(model) if model else None

    def get_all(self) -> List[Cliente]:
        """Obtener todos los clientes."""
        return [_model_to_domain(m) for m in ClienteModel.query.all()]

    def save(self, entity: Cliente) -> Cliente:
        """Guardar o actualizar un cliente."""
        if entity.id:
            model = ClienteModel.query.get(entity.id)
            if not model:
                raise ValueError(f"Cliente con id={entity.id} no encontrado")
        else:
            model = ClienteModel()
            db.session.add(model)

        model.codigo = entity.codigo
        model.nombre = entity.nombre
        model.email = entity.email
        model.telefono = entity.telefono
        model.direccion = entity.direccion
        model.activo = entity.activo
        model.organismo_id = entity.organismo_id
        model.tipo_cliente = entity.tipo_cliente

        db.session.flush()
        entity.id = model.id
        return entity

    def delete(self, id: int) -> bool:
        """Soft-delete: desactivar cliente."""
        model = ClienteModel.query.get(id)
        if not model:
            return False
        model.activo = False
        return True

    def get_by_codigo(self, codigo: str) -> Optional[Cliente]:
        """Obtener cliente por código único."""
        model = ClienteModel.query.filter_by(codigo=codigo).first()
        return _model_to_domain(model) if model else None

    def exists_by_codigo(self, codigo: str) -> bool:
        """Verificar si existe un cliente con el código dado."""
        return ClienteModel.query.filter_by(codigo=codigo).count() > 0

    def search(
        self,
        nombre: str = "",
        activo: Optional[bool] = None
    ) -> List[Cliente]:
        """Buscar clientes por nombre y/o estado."""
        query = ClienteModel.query
        if nombre:
            query = query.filter(ClienteModel.nombre.ilike(f"%{nombre}%"))
        if activo is not None:
            query = query.filter_by(activo=activo)
        return [_model_to_domain(m) for m in query.order_by(ClienteModel.nombre).all()]
