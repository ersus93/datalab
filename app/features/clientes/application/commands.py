"""
Feature: Clientes
Capa: Application - Casos de Uso (Commands)
Orquesta la lógica de negocio; no depende de Flask ni SQLAlchemy.
"""
from app.core.domain.base import NotFoundError, ValidationError
from app.features.clientes.application.dtos import (
    ActualizarClienteCommand,
    ClienteDTO,
    CrearClienteCommand,
)
from app.features.clientes.domain.models import Cliente
from app.features.clientes.domain.repositories import ClienteRepository


class CrearClienteHandler:
    """Caso de uso: Crear un nuevo cliente."""

    def __init__(self, repo: ClienteRepository):
        self.repo = repo

    def handle(self, cmd: CrearClienteCommand) -> ClienteDTO:
        if self.repo.exists_by_codigo(cmd.codigo):
            raise ValidationError(f"Ya existe un cliente con el código '{cmd.codigo}'.")

        cliente = Cliente(
            codigo=cmd.codigo,
            nombre=cmd.nombre,
            ruc_ci=cmd.ruc_ci,
            telefono=cmd.telefono,
            email=cmd.email,
            direccion=cmd.direccion,
        )
        saved = self.repo.save(cliente)
        return ClienteDTO.from_entity(saved)


class ActualizarClienteHandler:
    """Caso de uso: Actualizar datos de un cliente existente."""

    def __init__(self, repo: ClienteRepository):
        self.repo = repo

    def handle(self, cmd: ActualizarClienteCommand) -> ClienteDTO:
        cliente = self.repo.get_by_id(cmd.id)
        if not cliente:
            raise NotFoundError("Cliente", cmd.id)

        cliente.nombre = cmd.nombre
        cliente.ruc_ci = cmd.ruc_ci
        cliente.actualizar_contacto(cmd.telefono, cmd.email)
        cliente.direccion = cmd.direccion

        saved = self.repo.save(cliente)
        return ClienteDTO.from_entity(saved)


class DesactivarClienteHandler:
    """Caso de uso: Desactivar un cliente."""

    def __init__(self, repo: ClienteRepository):
        self.repo = repo

    def handle(self, cliente_id: int) -> ClienteDTO:
        cliente = self.repo.get_by_id(cliente_id)
        if not cliente:
            raise NotFoundError("Cliente", cliente_id)

        cliente.desactivar()
        saved = self.repo.save(cliente)
        return ClienteDTO.from_entity(saved)
