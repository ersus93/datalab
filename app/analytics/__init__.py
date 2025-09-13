"""Blueprint analytics para ONIE DataLab."""

from flask import Blueprint

analytics_bp = Blueprint('analytics', __name__)

from . import views