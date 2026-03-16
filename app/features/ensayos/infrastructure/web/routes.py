"""
Feature: Ensayos
Capa: Infrastructure - Web (Adapter Flask)
"""
from flask import Blueprint, jsonify, request

ensayos_bp = Blueprint("ensayos", __name__, url_prefix="/api/ensayos")


@ensayos_bp.get("/")
def listar_ensayos():
    return jsonify({"message": "Feature Ensayos - por implementar"}), 200


@ensayos_bp.post("/")
def crear_ensayo():
    return jsonify({"message": "Crear ensayo"}), 201


@ensayos_bp.patch("/<int:ensayo_id>/iniciar")
def iniciar_ensayo(ensayo_id: int):
    """Inicia el ensayo asignando un analista."""
    data = request.get_json()
    analista = data.get("analista", "")
    return jsonify({"message": f"Ensayo {ensayo_id} iniciado por {analista}"}), 200


@ensayos_bp.post("/<int:ensayo_id>/resultados")
def registrar_resultado(ensayo_id: int):
    """Registra un resultado de parámetro en el ensayo."""
    return jsonify({"message": f"Resultado registrado en ensayo {ensayo_id}"}), 201


@ensayos_bp.patch("/<int:ensayo_id>/completar")
def completar_ensayo(ensayo_id: int):
    return jsonify({"message": f"Ensayo {ensayo_id} completado"}), 200
