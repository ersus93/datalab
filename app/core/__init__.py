"""Blueprint core para funcionalidades principales de ONIE DataLab."""

from flask import Blueprint

core_bp = Blueprint('core', __name__)

from . import views