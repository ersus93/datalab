#!/usr/bin/env python3
"""Modelos de datos de referencia (lookup/catalog) para DataLab."""

from datetime import datetime
from app import db


class Area(db.Model):
    """Modelo de Área de laboratorio.
    
    Representa las diferentes áreas del laboratorio como FQ (Fisicoquímica),
    MB (Microbiología), ES (Evaluación Sensorial), OS (Otros).
    """
    
    __tablename__ = 'areas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), unique=True, nullable=False, index=True)
    
    # Timestamps
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    ensayos = db.relationship('Ensayo', back_populates='area', lazy=True)
    ensayos_es = db.relationship('EnsayoES', back_populates='area', lazy=True)
    
    def __repr__(self):
        return f'<Area {self.sigla}: {self.nombre}>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'sigla': self.sigla,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }


class Organismo(db.Model):
    """Modelo de Organismo/Entidad.
    
    Representa las organizaciones o entidades a las que pertenecen los clientes.
    """
    
    __tablename__ = 'organismos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), unique=True, nullable=False, index=True)
    
    # Timestamps
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    clientes = db.relationship('Cliente', back_populates='organismo', lazy=True)
    
    def __repr__(self):
        return f'<Organismo {self.nombre}>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }


class Provincia(db.Model):
    """Modelo de Provincia.
    
    Representa las provincias geográficas donde se ubican las fábricas.
    """
    
    __tablename__ = 'provincias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), unique=True, nullable=False, index=True)
    
    # Timestamps
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    fabricas = db.relationship('Fabrica', back_populates='provincia', lazy=True)
    
    def __repr__(self):
        return f'<Provincia {self.sigla}: {self.nombre}>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'sigla': self.sigla,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }


class Destino(db.Model):
    """Modelo de Destino de Producto.
    
    Representa los destinos de los productos:
    - CF: Consumo Familiar
    - AC: Alimentación Colectiva
    - ME: Menores
    - CD: Comercialización Directa
    - DE: Desechos
    """
    
    __tablename__ = 'destinos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), unique=True, nullable=False, index=True)
    
    # Timestamps
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    productos = db.relationship('Producto', back_populates='destino', lazy=True)
    
    def __repr__(self):
        return f'<Destino {self.sigla}: {self.nombre}>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'sigla': self.sigla,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }


class Rama(db.Model):
    """Modelo de Rama/Sector Industrial.
    
    Representa los sectores industriales como Carne, Lácteos, Bebidas, etc.
    """
    
    __tablename__ = 'ramas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Timestamps
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships (Phase 2 Issue #3)
    productos = db.relationship('Producto', back_populates='rama', lazy=True)
    
    def __repr__(self):
        return f'<Rama {self.nombre}>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }


class Mes(db.Model):
    """Modelo de Mes del Calendario.
    
    Representa los meses del año para reportes y estadísticas.
    """
    
    __tablename__ = 'meses'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    sigla = db.Column(db.String(5), nullable=False)
    
    # Timestamps
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Mes {self.id}: {self.nombre}>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'sigla': self.sigla,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }


class Anno(db.Model):
    """Modelo de Año.
    
    Representa los años disponibles para reportes y estadísticas.
    Permite activar/desactivar años según se necesiten.
    """
    
    __tablename__ = 'annos'
    
    anno = db.Column(db.String(4), primary_key=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Anno {self.anno} ({"activo" if self.activo else "inactivo"})>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'anno': self.anno,
            'activo': self.activo,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }


class TipoES(db.Model):
    """Modelo de Tipo de Evaluación Sensorial.
    
    Representa los diferentes tipos de evaluaciones sensoriales
    que se pueden realizar en el laboratorio.
    """
    
    __tablename__ = 'tipos_es'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Timestamps
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    ensayos_es = db.relationship('EnsayoES', back_populates='tipo_es', lazy=True)
    
    def __repr__(self):
        return f'<TipoES {self.nombre}>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }


class UnidadMedida(db.Model):
    """Modelo de Unidad de Medida.
    
    Representa las unidades de medida utilizadas en los ensayos
    y análisis de laboratorio (kg, g, mg, ml, l, etc.).
    """
    
    __tablename__ = 'unidades_medida'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(50), nullable=False)
    
    # Timestamps
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    pedidos = db.relationship('Pedido', back_populates='unidad_medida', lazy=True)
    
    def __repr__(self):
        return f'<UnidadMedida {self.codigo}: {self.nombre}>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }
