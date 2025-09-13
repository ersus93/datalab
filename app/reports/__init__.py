"""Blueprint reports para ONIE DataLab."""

from flask import Blueprint

reports_bp = Blueprint('reports', __name__)

from . import views