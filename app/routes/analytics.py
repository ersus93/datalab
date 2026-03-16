"""Rutas web para Analytics Dashboard."""
from flask import Blueprint, render_template
from flask_login import login_required

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/')
@login_required
def index():
    """Dashboard de análisis del laboratorio."""
    return render_template('pages/analytics/analytics.html')


@analytics_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard de análisis del laboratorio (alias)."""
    return render_template('pages/analytics/analytics.html')