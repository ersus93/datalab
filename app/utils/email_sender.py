"""
Utilidad para envío de correos electrónicos.
Soporta envío síncrono y asíncrono con plantillas HTML y texto.
"""
import logging
from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

logger = logging.getLogger(__name__)


def send_async_email(app, msg):
    """
    Envía un correo de forma asíncrona en un hilo separado.

    Args:
        app: Instancia de la aplicación Flask.
        msg: Objeto Message de Flask-Mail a enviar.
    """
    with app.app_context():
        try:
            mail = app.extensions.get('mail')
            if not mail:
                mail = getattr(app, 'mail', None)
            if mail:
                mail.send(msg)
                logger.info(f"Correo enviado asíncronamente a: {msg.recipients}")
            else:
                logger.error("Flask-Mail no está inicializado")
        except Exception as e:
            logger.error(f"Error al enviar correo asíncrono: {str(e)}")


def send_email(to, subject, template, **kwargs):
    """
    Envía un correo electrónico con versiones HTML y texto plano.

    Args:
        to: Dirección o lista de direcciones de correo destinatario(s).
        subject: Asunto del correo.
        template: Nombre base de la plantilla (sin extensión).
                 Se buscará {template}.html y {template}.txt
        **kwargs: Variables para renderizar en las plantillas.

    Returns:
        Thread: El hilo de ejecución si se envía asíncronamente, None en caso de error.
    """
    try:
        app = current_app._get_current_object()

        # Normalizar destinatarios a lista
        if isinstance(to, str):
            recipients = [to]
        else:
            recipients = list(to)

        msg = Message(
            subject=subject,
            recipients=recipients
        )

        # Renderizar cuerpo en texto plano
        try:
            msg.body = render_template(f'{template}.txt', **kwargs)
        except Exception:
            msg.body = None

        # Renderizar cuerpo en HTML
        try:
            msg.html = render_template(f'{template}.html', **kwargs)
        except Exception:
            msg.html = None

        # Si no hay plantilla HTML pero sí texto, usar texto como HTML básico
        if msg.body and not msg.html:
            msg.html = f"<pre>{msg.body}</pre>"

        # Si no hay contenido, registrar error
        if not msg.body and not msg.html:
            logger.error(f"No se encontraron plantillas para: {template}")
            return None

        # Enviar asíncronamente
        thr = Thread(target=send_async_email, args=[app, msg])
        thr.start()
        logger.info(f"Correo encolado para envío a: {recipients}")
        return thr

    except Exception as e:
        logger.error(f"Error al preparar correo: {str(e)}")
        return None
