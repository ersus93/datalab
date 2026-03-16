"""Servicio para importar datos desde Access RM2026."""
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from decimal import Decimal

from app import db

logger = logging.getLogger(__name__)


class AccessImporter:
    """
    Importador de datos desde Microsoft Access.

    Características:
    - Conexión vía pyodbc
    - Mapeo de campos Access -> PostgreSQL
    - Transformación de tipos (BIT -> Boolean, CURRENCY -> Numeric)
    - Validación de integridad referencial
    - Reporte de estadísticas
    """

    TABLE_MAPPING = {
        'reference': {
            'Areas': {
                'model_class': 'Area',
                'fields': {'IdArea': 'id', 'Area': 'nombre', 'Sigla': 'sigla'}
            },
            'Organismos': {
                'model_class': 'Organismo',
                'fields': {'IdOrg': 'id', 'Organismo': 'nombre'}
            },
            'Provincias': {
                'model_class': 'Provincia',
                'fields': {'IdProv': 'id', 'Provincia': 'nombre', 'Sigla': 'sigla'}
            },
            'Destinos': {
                'model_class': 'Destino',
                'fields': {'IdDest': 'id', 'Destino': 'nombre', 'Sigla': 'sigla'}
            },
            'Ramas': {
                'model_class': 'Rama',
                'fields': {'IdRama': 'id', 'Rama': 'nombre'}
            },
            'Meses': {
                'model_class': 'Mes',
                'fields': {'IdMes': 'id', 'Mes': 'nombre', 'Sigla': 'sigla'}
            },
            'Annos': {
                'model_class': 'Anno',
                'fields': {'Anno': 'anno', 'Activo': 'activo'}
            },
            'TipoES': {
                'model_class': 'TipoES',
                'fields': {'IdTipoES': 'id', 'TipoES': 'nombre'}
            },
            'UnidadesMedida': {
                'model_class': 'UnidadMedida',
                'fields': {'IdUM': 'id', 'Codigo': 'codigo', 'UnidadMedida': 'nombre'}
            }
        },
        'master': {
            'Clientes': {
                'model_class': 'Cliente',
                'fields': {
                    'IdCliente': 'id',
                    'Codigo': 'codigo',
                    'Cliente': 'nombre',
                    'Correo': 'email',
                    'Telefono': 'telefono',
                    'Direccion': 'direccion',
                    'IdOrg': 'organismo_id',
                    'TipoCliente': 'tipo_cliente',
                    'Activo': 'activo'
                }
            },
            'Fabricas': {
                'model_class': 'Fabrica',
                'fields': {
                    'IdFabrica': 'id',
                    'IdCliente': 'cliente_id',
                    'Fabrica': 'nombre',
                    'IdProv': 'provincia_id',
                    'Activo': 'activo'
                }
            },
            'Productos': {
                'model_class': 'Producto',
                'fields': {
                    'IdProd': 'id',
                    'Producto': 'nombre',
                    'IdDest': 'destino_id',
                    'Activo': 'activo'
                }
            }
        },
        'test': {
            'Ensayos': {
                'model_class': 'Ensayo',
                'fields': {
                    'IdEns': 'id',
                    'NomOfic': 'nombre_oficial',
                    'NomEns': 'nombre_corto',
                    'IdArea': 'area_id',
                    'Precio': 'precio',
                    'UM': 'unidad_medida',
                    'Activo': 'activo',
                    'EsEnsayo': 'es_ensayo'
                }
            },
            'EnsayosES': {
                'model_class': 'EnsayoES',
                'fields': {
                    'IdEnsES': 'id',
                    'NomOfic': 'nombre_oficial',
                    'NomEnsES': 'nombre_corto',
                    'IdArea': 'area_id',
                    'IdTipoES': 'tipo_es_id',
                    'Precio': 'precio',
                    'UM': 'unidad_medida',
                    'Activo': 'activo'
                }
            },
            'EnsayosXProductos': {
                'model_class': 'EnsayoXProducto',
                'fields': {
                    'IdProd': 'producto_id',
                    'IdEns': 'ensayo_id'
                }
            }
        }
    }

    EXPECTED_COUNTS = {
        'Areas': 4,
        'Organismos': 5,
        'Provincias': 16,
        'Destinos': 5,
        'Ramas': 8,
        'Meses': 12,
        'Annos': 5,
        'TipoES': 4,
        'UnidadesMedida': 14,
        'Clientes': 166,
        'Fabricas': 403,
        'Productos': 160,
        'Ensayos': 143,
        'EnsayosES': 29,
        'EnsayosXProductos': 500
    }

    def __init__(self, access_db_path: str, dry_run: bool = False):
        self.access_db_path = access_db_path
        self.dry_run = dry_run
        self.stats = {
            'inserted': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        self._access_conn = None
        self._model_cache: Dict[str, Any] = {}

    def connect_to_access(self):
        """Establecer conexión a Access vía pyodbc."""
        try:
            import pyodbc
            conn_str = (
                r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                r'DBQ=' + self.access_db_path + ';'
            )
            self._access_conn = pyodbc.connect(conn_str)
            logger.info(f"Conectado a Access: {self.access_db_path}")
            return self._access_conn
        except ImportError:
            logger.error("pyodbc no está instalado. Instalar con: pip install pyodbc")
            raise
        except Exception as e:
            logger.error(f"Error conectando a Access: {e}")
            raise

    def _get_model_class(self, model_name: str):
        """Obtener clase de modelo por nombre (con cache)."""
        if model_name not in self._model_cache:
            from app.database.models import reference, cliente, fabrica, producto, ensayo, ensayo_es, ensayo_x_producto

            model_map = {
                'Area': reference.Area,
                'Organismo': reference.Organismo,
                'Provincia': reference.Provincia,
                'Destino': reference.Destino,
                'Rama': reference.Rama,
                'Mes': reference.Mes,
                'Anno': reference.Anno,
                'TipoES': reference.TipoES,
                'UnidadMedida': reference.UnidadMedida,
                'Cliente': cliente.Cliente,
                'Fabrica': fabrica.Fabrica,
                'Producto': producto.Producto,
                'Ensayo': ensayo.Ensayo,
                'EnsayoES': ensayo_es.EnsayoES,
                'EnsayoXProducto': ensayo_x_producto.EnsayoXProducto,
            }

            if model_name not in model_map:
                raise ValueError(f"Modelo no encontrado: {model_name}")

            self._model_cache[model_name] = model_map[model_name]

        return self._model_cache[model_name]

    def _transform_value(self, value: Any, field_name: str) -> Any:
        """Transformar valores de Access a PostgreSQL."""
        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            if field_name in ('activo', 'es_ensayo'):
                return bool(value)
            return value

        if isinstance(value, float):
            if field_name in ('precio',):
                return Decimal(str(value))
            return value

        if isinstance(value, str):
            value = value.strip()
            if field_name in ('activo', 'es_ensayo'):
                return value.lower() in ('true', '1', 'yes', 'si', '-1')
            return value if value else None

        if hasattr(value, 'strftime'):
            return value

        return value

    def _fetch_access_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Obtener datos desde Access."""
        if self._access_conn is None:
            self.connect_to_access()

        cursor = self._access_conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM [{table_name}]")
            columns = [desc[0] for desc in cursor.description]
            rows = []
            for row in cursor.fetchall():
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i]
                rows.append(row_dict)
            return rows
        except Exception as e:
            logger.error(f"Error leyendo tabla {table_name}: {e}")
            raise
        finally:
            cursor.close()

    def _map_row_to_model(self, row: Dict[str, Any], field_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Mapear fila de Access a diccionario de modelo."""
        result = {}
        for access_field, model_field in field_mapping.items():
            if access_field in row:
                value = row[access_field]
                transformed = self._transform_value(value, model_field)
                result[model_field] = transformed
        return result

    def _import_table(self, access_table: str, config: Dict[str, Any]) -> Dict[str, int]:
        """Importar una tabla específica."""
        model_class = self._get_model_class(config['model_class'])
        field_mapping = config['fields']

        logger.info(f"Importando {access_table} -> {config['model_class']}...")

        try:
            rows = self._fetch_access_data(access_table)
        except Exception as e:
            logger.error(f"No se pudo leer tabla {access_table}: {e}")
            return {'inserted': 0, 'updated': 0, 'skipped': 0, 'errors': 1}

        table_stats = {'inserted': 0, 'updated': 0, 'skipped': 0, 'errors': 0}

        for row in rows:
            try:
                data = self._map_row_to_model(row, field_mapping)

                pk_field = 'id'
                pk_value = data.get(pk_field)

                if pk_value is None and 'anno' in data:
                    pk_field = 'anno'
                    pk_value = data.get('anno')

                existing = None
                if pk_value is not None:
                    existing = model_class.query.get(pk_value)

                if self.dry_run:
                    if existing:
                        table_stats['skipped'] += 1
                    else:
                        table_stats['inserted'] += 1
                    continue

                if existing:
                    for key, value in data.items():
                        if key != pk_field and hasattr(existing, key):
                            setattr(existing, key, value)
                    table_stats['updated'] += 1
                else:
                    new_record = model_class(**data)
                    db.session.add(new_record)
                    table_stats['inserted'] += 1

            except Exception as e:
                logger.error(f"Error procesando fila en {access_table}: {e}")
                table_stats['errors'] += 1

        if not self.dry_run:
            try:
                db.session.commit()
            except Exception as e:
                logger.error(f"Error en commit para {access_table}: {e}")
                db.session.rollback()
                table_stats['errors'] += table_stats['inserted'] + table_stats['updated']
                table_stats['inserted'] = 0
                table_stats['updated'] = 0

        expected = self.EXPECTED_COUNTS.get(access_table, len(rows))
        logger.info(
            f"{access_table}: {table_stats['inserted']} insertados, "
            f"{table_stats['updated']} actualizados, "
            f"{table_stats['skipped']} omitidos, "
            f"{table_stats['errors']} errores "
            f"(esperados: {expected})"
        )

        return table_stats

    def import_reference_data(self) -> Dict[str, Any]:
        """Importar 9 tablas de referencia (73 registros)."""
        logger.info("=== Importando datos de referencia ===")

        total_stats = {'inserted': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        results = {}

        for access_table, config in self.TABLE_MAPPING['reference'].items():
            stats = self._import_table(access_table, config)
            results[access_table] = stats

            for key in total_stats:
                total_stats[key] += stats.get(key, 0)

        self.stats.update(total_stats)
        return {'total': total_stats, 'tables': results}

    def import_master_data(self) -> Dict[str, Any]:
        """Importar 3 tablas maestras (729 registros)."""
        logger.info("=== Importando datos maestros ===")

        total_stats = {'inserted': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        results = {}

        for access_table, config in self.TABLE_MAPPING['master'].items():
            stats = self._import_table(access_table, config)
            results[access_table] = stats

            for key in total_stats:
                total_stats[key] += stats.get(key, 0)

        self.stats.update(total_stats)
        return {'total': total_stats, 'tables': results}

    def import_test_catalogs(self) -> Dict[str, Any]:
        """Importar catálogos de ensayos (172 registros)."""
        logger.info("=== Importando catálogos de ensayos ===")

        total_stats = {'inserted': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        results = {}

        for access_table, config in self.TABLE_MAPPING['test'].items():
            stats = self._import_table(access_table, config)
            results[access_table] = stats

            for key in total_stats:
                total_stats[key] += stats.get(key, 0)

        self.stats.update(total_stats)
        return {'total': total_stats, 'tables': results}

    def validate_references(self) -> bool:
        """Validar integridad referencial después de importar."""
        logger.info("=== Validando integridad referencial ===")

        validation_checks = [
            ('Fabricas', 'cliente_id', 'Clientes', 'id'),
            ('Fabricas', 'provincia_id', 'Provincias', 'id'),
            ('Productos', 'destino_id', 'Destinos', 'id'),
            ('Ensayos', 'area_id', 'Areas', 'id'),
            ('EnsayosES', 'area_id', 'Areas', 'id'),
            ('EnsayosES', 'tipo_es_id', 'TipoES', 'id'),
            ('Clientes', 'organismo_id', 'Organismos', 'id'),
        ]

        all_valid = True

        for table, fk_field, ref_table, ref_field in validation_checks:
            try:
                model_class = self._get_model_class(self.TABLE_MAPPING['master'].get(table, {}).get('model_class') or
                                                    self.TABLE_MAPPING['test'].get(table, {}).get('model_class'))

                ref_model_class = self._get_model_class(
                    self.TABLE_MAPPING['reference'].get(ref_table, {}).get('model_class') or
                    self.TABLE_MAPPING['master'].get(ref_table, {}).get('model_class') or
                    ref_table.replace('s', '') if ref_table != 'Areas' else 'Area'
                )

                orphan_count = self._check_orphan_records(model_class, fk_field, ref_model_class, ref_field)

                if orphan_count > 0:
                    logger.warning(f"{table}: {orphan_count} registros huérfanos en {fk_field}")
                    all_valid = False
                else:
                    logger.info(f"{table}.{fk_field} -> {ref_table}.{ref_field}: OK")

            except Exception as e:
                logger.error(f"Error validando {table}.{fk_field}: {e}")
                all_valid = False

        return all_valid

    def _check_orphan_records(self, model_class, fk_field: str, ref_model_class, ref_field: str) -> int:
        """Contar registros huérfanos (FK que no apuntan a ningún registro)."""
        try:
            records = model_class.query.all()
            orphan_count = 0

            for record in records:
                fk_value = getattr(record, fk_field, None)
                if fk_value is not None:
                    ref_record = ref_model_class.query.get(fk_value)
                    if ref_record is None:
                        orphan_count += 1

            return orphan_count
        except Exception as e:
            logger.error(f"Error verificando huérfanos: {e}")
            return -1

    def get_stats(self) -> Dict[str, int]:
        """Obtener estadísticas de importación."""
        return self.stats.copy()

    def close(self):
        """Cerrar conexión a Access."""
        if self._access_conn:
            try:
                self._access_conn.close()
                logger.info("Conexión a Access cerrada")
            except Exception as e:
                logger.warning(f"Error cerrando conexión: {e}")
            finally:
                self._access_conn = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
