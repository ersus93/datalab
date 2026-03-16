"""Script de importación de datos para Phase 1-4.
Mapea columnas CSV a campos de base de datos.
"""
import sqlite3
import csv
from datetime import datetime

# Usar la base de datos correcta
conn = sqlite3.connect('instance/datalab.db')
cur = conn.cursor()
now = datetime.now().isoformat()

def clean_int(val):
    """Convierte a int, devuelve None si está vacío."""
    if val is None or val == '':
        return None
    try:
        return int(val)
    except:
        return None

def clean_str(val):
    """Limpia strings."""
    if val is None:
        return ''
    return str(val).strip()

def clean_bool(val):
    """Convierte a booleano."""
    if val is None or val == '':
        return 1  # Default activo
    return 1 if val.lower() in ['true', '1', 'yes'] else 0

def clean_float(val):
    """Convierte a float."""
    if val is None or val == '':
        return None
    try:
        return float(val.replace(',', '.'))
    except:
        return None

# ============ IMPORTAR CLIENTES ============
print('=== Importing Clientes ===')
with open('data/migrations/clientes.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        try:
            id_val = clean_int(row.get('IdCli'))
            if id_val is None:
                continue
            
            nombre = clean_str(row.get('NomCli'))
            organismo_id = clean_int(row.get('IdOrg'))
            tipo = clean_int(row.get('IdTipoCli')) or 1
            activo = clean_bool(row.get('CliActivo'))
            
            cur.execute(
                'INSERT OR REPLACE INTO clientes (id, nombre, codigo, organismo_id, tipo_cliente, activo, fecha_creacion) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (id_val, nombre, f'CLI{id_val}', organismo_id, tipo, activo, now)
            )
            count += 1
        except Exception as e:
            print(f'Error: {e}')
    print(f'Imported {count} clientes')

# ============ IMPORTAR FABRICAS ============
print('\n=== Importing Fabricas ===')
with open('data/migrations/fabricas.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        try:
            id_val = clean_int(row.get('IdFca'))
            if id_val is None:
                continue
                
            nombre = clean_str(row.get('NomFca'))
            provincia_id = clean_int(row.get('IdPro'))
            cliente_id = clean_int(row.get('IdCli'))
            
            cur.execute(
                'INSERT OR REPLACE INTO fabricas (id, nombre, codigo, cliente_id, provincia_id, activo, fecha_creacion) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (id_val, nombre, f'FAB{id_val}', cliente_id, provincia_id, 1, now)
            )
            count += 1
        except Exception as e:
            print(f'Error: {e}')
    print(f'Imported {count} fabricas')

# ============ IMPORTAR PRODUCTOS ============
print('\n=== Importing Productos ===')
with open('data/migrations/productos.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        try:
            id_val = clean_int(row.get('IdPro'))
            if id_val is None:
                continue
                
            nombre = clean_str(row.get('NomPro'))
            destino_id = clean_int(row.get('IdDest'))
            rama_id = clean_int(row.get('IdRama'))
            activo = clean_bool(row.get('ProActivo'))
            
            cur.execute(
                'INSERT OR REPLACE INTO productos (id, nombre, codigo, destino_id, rama_id, activo, fecha_creacion) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (id_val, nombre, f'PRO{id_val}', destino_id, rama_id, activo, now)
            )
            count += 1
        except Exception as e:
            print(f'Error: {e}')
    print(f'Imported {count} productos')

conn.commit()

# ============ VERIFICAR IMPORTACIÓN ============
print('\n=== Verificación ===')
cur.execute('SELECT COUNT(*) FROM clientes')
print(f'Clientes: {cur.fetchone()[0]}')

cur.execute('SELECT COUNT(*) FROM fabricas')
print(f'Fabricas: {cur.fetchone()[0]}')

cur.execute('SELECT COUNT(*) FROM productos')
print(f'Productos: {cur.fetchone()[0]}')

conn.close()
print('\nDone!')
