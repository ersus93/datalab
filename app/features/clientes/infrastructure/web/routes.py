"""
Feature: Clientes
Capa: Infrastructure - Web (Adapter Flask)
Blueprint Flask que actúa como adaptador de entrada (driving adapter).
"""
from flask import Blueprint, jsonify, request

from app.core.domain.base import NotFoundError, ValidationError
from app.core.infrastructure.database import db
from app.features.clientes.application.commands import (
    ActualizarClienteHandler,
    CrearClienteHandler,
    DesactivarClienteHandler,
)
from app.features.clientes.application.dtos import (
    ActualizarClienteCommand,
    CrearClienteCommand,
)
from app.features.clientes.application.queries import (
    ListarClientesQuery,
    ObtenerClienteQuery,
)
from app.features.clientes.infrastructure.persistence.sql_repository import (
    SQLClienteRepository,
)

clientes_bp = Blueprint("clientes", __name__, url_prefix="/api/clientes")


def _get_repo():
    return SQLClienteRepository(db.session)


# ──────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────

@clientes_bp.get("/")
def listar_clientes():
    nombre = request.args.get("nombre", "")
    solo_activos = request.args.get("activos", "true").lower() == "true"
    query = ListarClientesQuery(_get_repo())
    clientes = query.execute(nombre=nombre, solo_activos=solo_activos)
    return jsonify([c.to_dict() for c in clientes])


@clientes_bp.get("/<int:cliente_id>")
def obtener_cliente(cliente_id: int):
    try:
        query = ObtenerClienteQuery(_get_repo())
        cliente = query.execute(cliente_id)
        return jsonify(cliente.to_dict())
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404


@clientes_bp.post("/")
def crear_cliente():
    data = request.get_json()
    try:
        cmd = CrearClienteCommand(
            codigo=data["codigo"],
            nombre=data["nombre"],
            ruc_ci=data.get("ruc_ci"),
            telefono=data.get("telefono"),
            email=data.get("email"),
            direccion=data.get("direccion"),
        )
        handler = CrearClienteHandler(_get_repo())
        cliente = handler.handle(cmd)
        return jsonify(cliente.to_dict()), 201
    except (ValidationError, KeyError) as e:
        return jsonify({"error": str(e)}), 400


@clientes_bp.put("/<int:cliente_id>")
def actualizar_cliente(cliente_id: int):
    data = request.get_json()
    try:
        cmd = ActualizarClienteCommand(
            id=cliente_id,
            nombre=data["nombre"],
            ruc_ci=data.get("ruc_ci"),
            telefono=data.get("telefono"),
            email=data.get("email"),
            direccion=data.get("direccion"),
        )
        handler = ActualizarClienteHandler(_get_repo())
        cliente = handler.handle(cmd)
        return jsonify(cliente.to_dict())
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except (ValidationError, KeyError) as e:
        return jsonify({"error": str(e)}), 400


@clientes_bp.delete("/<int:cliente_id>")
def desactivar_cliente(cliente_id: int):
    try:
        handler = DesactivarClienteHandler(_get_repo())
        cliente = handler.handle(cliente_id)
        return jsonify(cliente.to_dict())
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
