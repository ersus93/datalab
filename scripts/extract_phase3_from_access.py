#!/usr/bin/env python3
"""Extraer datos transaccionales Phase 3 desde Access a CSV."""
import csv
import sys
from pathlib import Path

OUTPUT_DIR = Path('data/migrations/phase3')


def extract_table(conn, table_name, columns, output_file):
    """Extraer tabla de Access a CSV."""
    try:
        import pyodbc
    except ImportError:
        print("Error: pyodbc no instalado. Instalar con: pip install pyodbc")
        sys.exit(1)

    cursor = conn.cursor()
    cols_str = ', '.join(columns.keys())
    query = f"SELECT {cols_str} FROM [{table_name}]"

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
    except Exception as e:
        print(f"Error consultando {table_name}: {e}")
        return 0

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(columns.values()))
        writer.writeheader()

        for row in rows:
            row_dict = {}
            for i, (source_col, target_col) in enumerate(columns.items()):
                value = row[i]
                if isinstance(value, str):
                    value = value.strip()
                row_dict[target_col] = value
            writer.writerow(row_dict)

    print(f"✓ {table_name}: {len(rows)} filas -> {output_file}")
    return len(rows)


def main(access_db_path: str):
    """Extraer todas las tablas Phase 3."""
    try:
        import pyodbc
    except ImportError:
        print("Error: pyodbc no instalado")
        sys.exit(1)

    # Crear directorio de salida
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Conectar a Access
    conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={access_db_path}"
    try:
        conn = pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Error conectando a Access: {e}")
        sys.exit(1)

    print(f"Extrayendo desde: {access_db_path}")
    print("="*60)

    # Extraer Órdenes de Trabajo
    extract_table(conn, 'OrdenesTrabajo', {
        'Id': 'Id',
        'NroOfic': 'NroOfic',
        'IdCliente': 'IdCliente',
        'Descripcion': 'Descripcion',
        'Observaciones': 'Observaciones',
        'FechCreacion': 'FechCreacion'
    }, OUTPUT_DIR / 'ordenes_trabajo.csv')

    # Extraer Pedidos
    extract_table(conn, 'Pedidos', {
        'IdPedido': 'IdPedido',
        'IdCliente': 'IdCliente',
        'IdProducto': 'IdProducto',
        'IdOrdenTrabajo': 'IdOrdenTrabajo',
        'Lote': 'Lote',
        'FechFab': 'FechFab',
        'FechVenc': 'FechVenc',
        'Cantidad': 'Cantidad',
        'IdUnidadMedida': 'IdUnidadMedida',
        'Observaciones': 'Observaciones',
        'FechPedido': 'FechPedido'
    }, OUTPUT_DIR / 'pedidos.csv')

    # Extraer Entradas
    extract_table(conn, 'Entradas', {
        'Id': 'Id',
        'IdPedido': 'IdPedido',
        'IdProducto': 'IdProducto',
        'IdFabrica': 'IdFabrica',
        'IdCliente': 'IdCliente',
        'IdRama': 'IdRama',
        'Codigo': 'Codigo',
        'Lote': 'Lote',
        'NroParte': 'NroParte',
        'CantidadRecib': 'CantidadRecib',
        'CantidadEntreg': 'CantidadEntreg',
        'CantidadMuest': 'CantidadMuest',
        'IdUnidadMedida': 'IdUnidadMedida',
        'FechFab': 'FechFab',
        'FechVenc': 'FechVenc',
        'FechMuestreo': 'FechMuestreo',
        'FechEntrada': 'FechEntrada',
        'Status': 'Status',
        'EnOS': 'EnOS',
        'Anulado': 'Anulado',
        'EntEntregada': 'EntEntregada',
        'Observaciones': 'Observaciones'
    }, OUTPUT_DIR / 'entradas.csv')

    conn.close()
    print("="*60)
    print("Extracción completada!")
    print(f"Archivos en: {OUTPUT_DIR}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extraer datos Phase 3 de Access')
    parser.add_argument('--access-db', required=True, help='Ruta a RM2026.accdb')
    args = parser.parse_args()

    main(args.access_db)
