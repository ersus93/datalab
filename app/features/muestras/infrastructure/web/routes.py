"""
Feature: Muestras
Capa: Infrastructure - Web (Adapter Flask)
"""
from flask import Blueprint, jsonify, request

from app.core.domain.base import NotFoundError, ValidationError
from app.core.infrastructure.database import db

muestras_bp = Blueprint("muestras", __name__, url_prefix="/api/muestras")

# Importaciones lazy para evitar circularidad (se completan al implementar)
def _get_repo():
    from app.features.muestras.infrastructure.persistence.sql_repository import SQLMuestraRepository
    return SQLMuestraRepository(db.session)


@muestras_bp.get("/")
def listar_muestras():
    """Lista muestras con filtros opcionales."""
    # TODO: Implementar query handler
    return jsonify({"message": "Feature Muestras - por implementar"}), 200


@muestras_bp.get("/<int:muestra_id>")
def obtener_muestra(muestra_id: int):
    return jsonify({"message": f"Muestra {muestra_id} - por implementar"}), 200


@muestras_bp.post("/")
def crear_muestra():
    return jsonify({"message": "Crear muestra - por implementar"}), 201


@muestras_bp.patch("/<int:muestra_id>/iniciar-analisis")
def iniciar_analisis(muestra_id: int):
    """Transición de estado: RECIBIDA → EN_ANALISIS."""
    return jsonify({"message": f"Iniciar análisis muestra {muestra_id}"}), 200


@muestras_bp.patch("/<int:muestra_id>/completar")
def completar_muestra(muestra_id: int):
    """Transición de estado: EN_ANALISIS → COMPLETADA."""
    return jsonify({"message": f"Completar muestra {muestra_id}"}), 200
