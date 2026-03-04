"""
Feature: Clientes
Capa: Application
Servicios de aplicación para gestión de clientes.
"""
from typing import List, Optional

from app.core.domain.base import NotFoundError, ValidationError
from app.features.clientes.domain.models import Cliente


class ClienteService:
    """Servicio de aplicación para operaciones con clientes."""

    def __init__(self, repository):
        self._repo = repository

    def crear_cliente(
        self,
        codigo: str,
        nombre: str,
        email: Optional[str] = None,
        telefono: Optional[str] = None,
        direccion: Optional[str] = None,
        organismo_id: Optional[int] = None,
        tipo_cliente: Optional[int] = None
    ) -> Cliente:
        """Crear un nuevo cliente."""
        cliente = Cliente(
            codigo=codigo,
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion,
            organismo_id=organismo_id,
            tipo_cliente=tipo_cliente
        )
        return self._repo.save(cliente)

    def obtener_cliente(self, cliente_id: int) -> Cliente:
        """Obtener cliente por ID."""
        cliente = self._repo.get_by_id(cliente_id)
        if not cliente:
            raise NotFoundError("Cliente", cliente_id)
        return cliente

    def listar_clientes(
        self,
        activo: Optional[bool] = None,
        organismo_id: Optional[int] = None
    ) -> List[Cliente]:
        """Listar clientes con filtros opcionales."""
        clientes = self._repo.list_all()
        
        if activo is not None:
            clientes = [c for c in clientes if c.activo == activo]
        if organismo_id is not None:
            clientes = [c for c in clientes if c.organismo_id == organismo_id]
            
        return clientes

    def actualizar_cliente(
        self,
        cliente_id: int,
        nombre: Optional[str] = None,
        email: Optional[str] = None,
        telefono: Optional[str] = None,
        direccion: Optional[str] = None,
        organismo_id: Optional[int] = None,
        tipo_cliente: Optional[int] = None
    ) -> Cliente:
        """Actualizar datos de un cliente existente."""
        cliente = self.obtener_cliente(cliente_id)
        
        if nombre is not None:
            cliente.nombre = nombre
        if email is not None:
            cliente.email = email
        if telefono is not None:
            cliente.telefono = telefono
        if direccion is not None:
            cliente.direccion = direccion
        if organismo_id is not None:
            cliente.organismo_id = organismo_id
        if tipo_cliente is not None:
            cliente.tipo_cliente = tipo_cliente
            
        # Re-validar el cliente actualizado
        cliente._validar()
        return self._repo.save(cliente)

    def desactivar_cliente(self, cliente_id: int) -> Cliente:
        """Desactivar un cliente (soft delete)."""
        cliente = self.obtener_cliente(cliente_id)
        cliente.desactivar()
        return self._repo.save(cliente)

    def activar_cliente(self, cliente_id: int) -> Cliente:
        """Activar un cliente."""
        cliente = self.obtener_cliente(cliente_id)
        cliente.activar()
        return self._repo.save(cliente)
