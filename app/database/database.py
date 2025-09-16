#!/usr/bin/env python3
"""Gestión de base de datos para DataLab."""

import os
import logging
from datetime import datetime
from flask import current_app
from app import db
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Configurar logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de operaciones de base de datos."""
    
    @staticmethod
    def init_database():
        """Inicializar la base de datos creando todas las tablas."""
        try:
            logger.info("Iniciando creación de tablas de base de datos...")
            db.create_all()
            logger.info("Tablas creadas exitosamente.")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error al crear tablas: {str(e)}")
            return False
    
    @staticmethod
    def drop_all_tables():
        """Eliminar todas las tablas de la base de datos."""
        try:
            logger.warning("Eliminando todas las tablas de la base de datos...")
            db.drop_all()
            logger.info("Tablas eliminadas exitosamente.")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error al eliminar tablas: {str(e)}")
            return False
    
    @staticmethod
    def reset_database():
        """Resetear la base de datos (eliminar y recrear todas las tablas)."""
        try:
            logger.info("Reseteando base de datos...")
            DatabaseManager.drop_all_tables()
            DatabaseManager.init_database()
            logger.info("Base de datos reseteada exitosamente.")
            return True
        except Exception as e:
            logger.error(f"Error al resetear base de datos: {str(e)}")
            return False
    
    @staticmethod
    def check_database_connection():
        """Verificar la conexión a la base de datos."""
        try:
            # Ejecutar una consulta simple para verificar la conexión
            db.session.execute(text('SELECT 1'))
            logger.info("Conexión a base de datos verificada exitosamente.")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error de conexión a base de datos: {str(e)}")
            return False
    
    @staticmethod
    def get_database_info():
        """Obtener información sobre la base de datos."""
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            info = {
                'database_url': current_app.config.get('SQLALCHEMY_DATABASE_URI', 'No configurada'),
                'total_tables': len(tables),
                'tables': tables,
                'engine': str(db.engine.url),
                'connection_status': DatabaseManager.check_database_connection()
            }
            
            return info
        except Exception as e:
            logger.error(f"Error al obtener información de base de datos: {str(e)}")
            return None
    
    @staticmethod
    def get_table_info(table_name):
        """Obtener información detallada de una tabla específica."""
        try:
            inspector = inspect(db.engine)
            
            if table_name not in inspector.get_table_names():
                return None
            
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            info = {
                'table_name': table_name,
                'columns': columns,
                'indexes': indexes,
                'foreign_keys': foreign_keys,
                'total_columns': len(columns)
            }
            
            return info
        except Exception as e:
            logger.error(f"Error al obtener información de tabla {table_name}: {str(e)}")
            return None
    
    @staticmethod
    def backup_database(backup_path=None):
        """Crear un respaldo de la base de datos (solo para SQLite)."""
        try:
            db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
            
            if not db_url.startswith('sqlite'):
                logger.warning("Backup automático solo disponible para SQLite.")
                return False
            
            # Extraer la ruta del archivo de base de datos
            db_file = db_url.replace('sqlite:///', '')
            
            if not os.path.exists(db_file):
                logger.error(f"Archivo de base de datos no encontrado: {db_file}")
                return False
            
            if backup_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{db_file}.backup_{timestamp}"
            
            import shutil
            shutil.copy2(db_file, backup_path)
            
            logger.info(f"Backup creado exitosamente: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error al crear backup: {str(e)}")
            return False
    
    
    @staticmethod
    def execute_raw_query(query, params=None):
        """Ejecutar una consulta SQL raw de forma segura."""
        try:
            result = db.session.execute(text(query), params or {})
            db.session.commit()
            return result
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al ejecutar consulta: {str(e)}")
            raise e

# Funciones de conveniencia
def init_db():
    """Función de conveniencia para inicializar la base de datos."""
    return DatabaseManager.init_database()

def reset_db():
    """Función de conveniencia para resetear la base de datos."""
    return DatabaseManager.reset_database()



def check_db():
    """Función de conveniencia para verificar la conexión."""
    return DatabaseManager.check_database_connection()

def get_db_info():
    """Función de conveniencia para obtener información de la base de datos."""
    return DatabaseManager.get_database_info()