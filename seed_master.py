import sqlite3
import csv
from datetime import datetime

conn = sqlite3.connect('instance/datalab_dev.db')
cur = conn.cursor()
now = datetime.now().isoformat()

print('=== Importing Clientes ===')
# Import clientes
with open('data/migrations/clientes.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        try:
            organismo_id = int(row['organismo_id']) if row.get('organismo_id') and row['organismo_id'] else None
            tipo = int(row['tipo_cliente']) if row.get('tipo_cliente') and row['tipo_cliente'] else 1
            activo = bool(int(row['activo'])) if row.get('activo') else 1
            cur.execute(
                'INSERT OR REPLACE INTO clientes (id, nombre, codigo, organismo_id, tipo_cliente, activo, creado_en) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (int(row['id']), row['nombre'], row.get('codigo', f'CLI{row["id"]}'), organismo_id, tipo, activo, now)
            )
            count += 1
        except Exception as e:
            print(f'Error: {e}')
    print(f'Imported {count} clientes')

print('=== Importing Fabricas ===')
# Import fabricas
with open('data/migrations/fabricas.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        try:
            provincia_id = int(row['provincia_id']) if row.get('provincia_id') and row['provincia_id'] else None
            activo = bool(int(row['activo'])) if row.get('activo') else 1
            cur.execute(
                'INSERT OR REPLACE INTO fabricas (id, nombre, codigo, cliente_id, provincia_id, direccion, activo, creado_en) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (int(row['id']), row['nombre'], row.get('codigo', f'FAB{row["id"]}'), int(row['cliente_id']), provincia_id, row.get('direccion', ''), activo, now)
            )
            count += 1
        except Exception as e:
            print(f'Error: {e}')
    print(f'Imported {count} fabricas')

print('=== Importing Productos ===')
# Import productos
with open('data/migrations/productos.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        try:
            destino_id = int(row['destino_id']) if row.get('destino_id') and row['destino_id'] else None
            rama_id = int(row['rama_id']) if row.get('rama_id') and row['rama_id'] else None
            activo = bool(int(row['activo'])) if row.get('activo') else 1
            cur.execute(
                'INSERT OR REPLACE INTO productos (id, nombre, codigo, destino_id, rama_id, activo, creado_en) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (int(row['id']), row['nombre'], row.get('codigo', f'PRO{row["id"]}'), destino_id, rama_id, activo, now)
            )
            count += 1
        except Exception as e:
            print(f'Error: {e}')
    print(f'Imported {count} productos')

conn.commit()
print('Done!')

# Verify
cur.execute('SELECT COUNT(*) FROM clientes')
print('Clientes:', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM fabricas')
print('Fabricas:', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM productos')
print('Productos:', cur.fetchone()[0])
conn.close()
