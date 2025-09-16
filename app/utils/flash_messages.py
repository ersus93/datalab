#!/usr/bin/env python3
"""Utilidades para manejo de mensajes flash."""

from flask import get_flashed_messages
from markupsafe import Markup


def render_flash_messages():
    """
    Renderiza los mensajes flash en HTML.
    
    Returns:
        Markup: HTML seguro con los mensajes flash renderizados
    """
    messages = get_flashed_messages(with_categories=True)
    
    if not messages:
        return Markup('')
    
    html_parts = ['<div class="flash-messages">']
    
    for category, message in messages:
        # Determinar el icono según la categoría
        if category == 'success':
            icon = '''<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>'''
            label = 'Éxito:'
        elif category == 'error':
            icon = '''<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>'''
            label = 'Error:'
        elif category == 'warning':
            icon = '''<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                      </svg>'''
            label = 'Advertencia:'
        else:
            icon = '''<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>'''
            label = 'Info:'
        
        # Construir el HTML del mensaje
        alert_class = 'error' if category == 'error' else category
        
        message_html = f'''
            <div class="alert alert-{alert_class}" role="alert">
                <div class="alert-content">
                    <div class="alert-icon">
                        {icon}
                    </div>
                    <div class="alert-text">
                        <strong>{label}</strong>
                        {message}
                    </div>
                </div>
                <button class="alert-close" aria-label="Cerrar alerta">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        '''
        
        html_parts.append(message_html)
    
    html_parts.append('</div>')
    
    return Markup(''.join(html_parts))


def flash_message_component():
    """
    Función helper para usar en templates Jinja2.
    
    Returns:
        Markup: HTML renderizado de los mensajes flash
    """
    return render_flash_messages()