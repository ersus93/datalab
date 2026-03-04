"""
Feature: Clientes
Capa: Application
Handlers para comandos (CQRS - Command side).
"""
from app.core.domain.base import NotFoundError, ValidationError
from app.features.clientes.application.dtos import (
    ActualizarClienteCommand,
    ClienteDTO,
    CrearClienteCommand,
)
from app.features.clientes.domain.models import Cliente


class CrearClienteHandler:
    """Handler para el comando CrearClienteCommand."""

    def __init__(self, repository):
        self._repo = repository

    def handle(self, cmd: CrearClienteCommand) -> ClienteDTO:
        """Crear un nuevo cliente."""
        # Verificar código duplicado
        if self._repo.exists_by_codigo(cmd.codigo):
            raise ValidationError(f"Ya existe un cliente con el código '{cmd.codigo}'.")

        # Crear entidad de dominio
        cliente = Cliente(
            codigo=cmd.codigo,
            nombre=cmd.nombre,
            email=cmd.email,
            telefono=cmd.telefono,
            direccion=cmd.direccion,
            organismo_id=cmd.organismo_id,
            tipo_cliente=cmd.tipo_cliente,
        )

        # Persistir
        guardado = self._repo.save(cliente)

        # Retornar DTO
        return ClienteDTO(
            id=guardado.id,
            codigo=guardado.codigo,
            nombre=guardado.nombre,
            email=guardado.email,
            telefono=guardado.telefono,
            direccion=guardado.direccion,
            activo=guardado.activo,
            organismo_id=guardado.organismo_id,
            tipo_cliente=guardado.tipo_cliente,
        )


class ActualizarClienteHandler:
    """Handler para el comando ActualizarClienteCommand."""

    def __init__(self, repository):
        self._repo = repository

    def handle(self, cmd: ActualizarClienteCommand) -> ClienteDTO:
        """Actualizar un cliente existente."""
        # Obtener cliente
        cliente = self._repo.get_by_id(cmd.id)
        if not cliente:
            raise NotFoundError("Cliente", cmd.id)

        # Actualizar campos si se proporcionan
        if cmd.nombre is not None:
            cliente.nombre = cmd.nombre
        if cmd.email is not None:
            cliente.email = cmd.email
        if cmd.telefono is not None:
            cliente.telefono = cmd.telefono
        if cmd.direccion is not None:
            cliente.direccion = cmd.direccion
        if cmd.organismo_id is not None:
            cliente.organismo_id = cmd.organismo_id
        if cmd.tipo_cliente is not None:
            cliente.tipo_cliente = cmd.tipo_cliente

        # Re-validar
        cliente._validar()

        # Persistir
        guardado = self._repo.save(cliente)

        # Retornar DTO
        return ClienteDTO(
            id=guardado.id,
            codigo=guardado.codigo,
            nombre=guardado.nombre,
            email=guardado.email,
            telefono=guardado.telefono,
            direccion=guardado.direccion,
            activo=guardado.activo,
            organismo_id=guardado.organismo_id,
            tipo_cliente=guardado.tipo_cliente,
        )


class DesactivarClienteHandler:
    """Handler para desactivar un cliente (soft delete)."""

    def __init__(self, repository):
        self._repo = repository

    def handle(self, cliente_id: int) -> ClienteDTO:
        """Desactivar un cliente."""
        # Obtener cliente
        cliente = self._repo.get_by_id(cliente_id)
        if not cliente:
            raise NotFoundError("Cliente", cliente_id)

        # Desactivar
        cliente.desactivar()

        # Persistir
        guardado = self._repo.save(cliente)

        # Retornar DTO
        return ClienteDTO(
            id=guardado.id,
            codigo=guardado.codigo,
            nombre=guardado.nombre,
            email=guardado.email,
            telefono=guardado.telefono,
            direccion=guardado.direccion,
            activo=guardado.activo,
            organismo_id=guardado.organismo_id,
            tipo_cliente=guardado.tipo_cliente,
        )
