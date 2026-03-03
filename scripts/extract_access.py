#!/usr/bin/env python3
"""Extraer datos desde Access RM2026 a CSV."""
import csv
import sys
import os
from pathlib import Path

# No hardcodear ruta - usar variable de entorno o argumento
DEFAULT_ACCESS_PATH = os.getenv('ACCESS_DB_PATH', '')
OUTPUT_DIR = Path("data/migrations")


def extract_table(conn, table_name, columns, output_dir):
    """Extraer tabla de Access a CSV."""
    try:
        import pyodbc
    except ImportError:
        print("Error: pyodbc no instalado. Instalar con: pip install pyodbc")
        sys.exit(1)

    cursor = conn.cursor()
    cols_str = ', '.join(columns.keys())
    query = f"SELECT {cols_str} FROM [{table_name}]"

    cursor.execute(query)
    rows = cursor.fetchall()

    output_file = output_dir / f"{table_name.lower()}.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns.values())
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


def main(access_path=None):
    """Extraer todas las tablas maestras."""
    access_path = access_path or DEFAULT_ACCESS_PATH

    if not access_path:
        print("Error: No se especificó ruta de Access. Use --access-db o variable ACCESS_DB_PATH")
        sys.exit(1)

    try:
        import pyodbc
    except ImportError:
        print("Error: pyodbc no instalado")
        sys.exit(1)

    if not os.path.exists(access_path):
        print(f"Error: Archivo no encontrado: {access_path}")
        sys.exit(1)

    # Crear directorio de salida
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Conectar a Access
    conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={access_path}"
    conn = pyodbc.connect(conn_str)

    print(f"Extrayendo desde: {access_path}")
    print("="*50)

    # Extraer Clientes
    extract_table(conn, 'Clientes', {
        'IdCli': 'id',
        'NomCli': 'nombre',
        'IdOrg': 'organismo_id',
        'IdTipoCli': 'tipo_cliente',
        'CliActivo': 'activo'
    }, OUTPUT_DIR)

    # Extraer Fabricas
    extract_table(conn, 'Fabricas', {
        'IdFca': 'id',
        'IdCli': 'cliente_id',
        'Fabrica': 'nombre',
        'IdProv': 'provincia_id'
    }, OUTPUT_DIR)

    # Extraer Productos
    extract_table(conn, 'Productos', {
        'IdProd': 'id',
        'Producto': 'nombre',
        'IdDest': 'destino_id'
    }, OUTPUT_DIR)

    conn.close()
    print("="*50)
    print("Extracción completada!")
    print(f"Archivos en: {OUTPUT_DIR}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extraer datos de Access')
    parser.add_argument('--access-db', help='Ruta a la base de datos Access')
    args = parser.parse_args()

    main(args.access_db)
