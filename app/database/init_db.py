#!/usr/bin/env python3
"""Script para inicializar la base de datos con los modelos básicos."""

import os
from app import create_app, db
from app.database.database import init_database
from app.database.models import Cliente, Pedido, OrdenTrabajo

def seed_sample_data():
    """Insertar datos de ejemplo en la base de datos."""
    try:
        # Verificar si ya existen datos
        if Cliente.query.first():
            print("Ya existen datos en la base de datos.")
            return True
        
        # Cliente de ejemplo
        cliente = Cliente(
            codigo='ONIE-001',
            nombre='Oficina Nacional de Inspección Estatal',
            email='contacto@onie.gob.cu',
            telefono='+53-7-123-4567',
            direccion='La Habana, Cuba'
        )
        db.session.add(cliente)
        db.session.flush()  # Para obtener el ID
        
        # Segundo cliente
        cliente2 = Cliente(
            codigo='LAB-002',
            nombre='Laboratorio Central de Alimentos',
            email='lab@alimentos.cu',
            telefono='+53-7-987-6543',
            direccion='Santiago de Cuba, Cuba'
        )
        db.session.add(cliente2)
        db.session.flush()
        
        # Pedidos de ejemplo
        pedido1 = Pedido(
            numero_pedido='PED-001-2024',
            descripcion='Análisis microbiológico de muestras de agua potable para verificación de calidad',
            cliente_id=cliente.id
        )
        db.session.add(pedido1)
        db.session.flush()
        
        pedido2 = Pedido(
            numero_pedido='PED-002-2024',
            descripcion='Análisis fisicoquímico de productos lácteos',
            cliente_id=cliente2.id
        )
        db.session.add(pedido2)
        db.session.flush()
        
        # Órdenes de trabajo de ejemplo
        orden1 = OrdenTrabajo(
            numero='OT-001-2024',
            descripcion='Análisis de coliformes totales y E. coli en muestras de agua',
            tipo_analisis='Microbiológico',
            pedido_id=pedido1.id
        )
        db.session.add(orden1)
        
        orden2 = OrdenTrabajo(
            numero='OT-002-2024',
            descripcion='Determinación de grasa, proteína y humedad en leche',
            tipo_analisis='Fisicoquímico',
            pedido_id=pedido2.id
        )
        db.session.add(orden2)
        
        orden3 = OrdenTrabajo(
            numero='OT-003-2024',
            descripcion='Análisis de metales pesados en agua',
            tipo_analisis='Químico',
            pedido_id=pedido1.id
        )
        db.session.add(orden3)
        
        db.session.commit()
        print("Datos de ejemplo insertados exitosamente.")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al insertar datos de ejemplo: {str(e)}")
        return False

def init_db_script():
    """Inicializar la base de datos con modelos y datos de ejemplo."""
    app = create_app()
    
    with app.app_context():
        print("Inicializando base de datos...")
        
        # Inicializar la base de datos
        if init_database():
            print("Tablas creadas exitosamente.")
        else:
            print("Error al crear las tablas.")
            return
        
        # Insertar datos de ejemplo
        print("Insertando datos de ejemplo...")
        if seed_sample_data():
            print("Datos de ejemplo insertados exitosamente.")
        else:
            print("Error al insertar datos de ejemplo.")
        
        print("Base de datos inicializada correctamente.")

if __name__ == '__main__':
    init_db_script()