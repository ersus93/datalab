#!/usr/bin/env python3
"""Modelo PlantillaInforme - Plantillas para generación de informes."""

from datetime import datetime

from app import db
from app.database.models.informe import TipoInforme


class PlantillaInforme(db.Model):
    """Plantilla para generación de informes.

    Define las plantillas personalizables usadas para generar informes
    técnicos y certificados. Incluye opciones de personalización visual
    como header, footer, CSS y logos.

    Attributes:
        id: Clave primaria.
        nombre: Nombre identificador de la plantilla.
        tipo: Tipo de informe según TipoInforme.
        header_html: Contenido HTML para el encabezado del informe.
        footer_html: Contenido HTML para el pie del informe.
        body_template: Plantilla Jinja2 para el cuerpo del informe.
        css_styles: Estilos CSS personalizados.
        logo_encabezado: Ruta al logo del encabezado.
        logo_pie: Ruta al logo del pie de página.
        activa: Flag que indica si la plantilla está activa.
        created_at: Timestamp de creación del registro.
        updated_at: Timestamp de última modificación.
    """

    __tablename__ = "plantillas_informe"

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(100), nullable=False)

    tipo = db.Column(
        db.Enum(
            TipoInforme,
            name="plantilla_tipo_informe",
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )

    header_html = db.Column(db.Text, nullable=True, default="")
    footer_html = db.Column(db.Text, nullable=True, default="")
    body_template = db.Column(db.Text, nullable=True, default="")
    css_styles = db.Column(db.Text, nullable=True, default="")

    logo_encabezado = db.Column(db.String(255), nullable=True)
    logo_pie = db.Column(db.String(255), nullable=True)

    activa = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<PlantillaInforme {self.nombre} ({self.tipo})>"

    def to_dict(self):
        """Serializa la plantilla a diccionario.

        Returns:
            dict: Representación del registro con todos los campos.
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "header_html": self.header_html,
            "footer_html": self.footer_html,
            "body_template": self.body_template,
            "css_styles": self.css_styles,
            "logo_encabezado": self.logo_encabezado,
            "logo_pie": self.logo_pie,
            "activa": self.activa,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
