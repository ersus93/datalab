import sqlite3
import csv
from datetime import datetime

conn = sqlite3.connect('instance/datalab_dev.db')
cur = conn.cursor()
now = datetime.now().isoformat()

print('=== Importing Clientes ===')
# Import clientes - map column names
with open('data/migrations/clientes.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    # Normalize column names
    fieldnames = [name.strip().replace('\ufeff', '').replace('"', '') for name in reader.fieldnames]
    print(f'Columns: {fieldnames}')
    
    count = 0
    for row in reader:
        try:
            # Map columns: IdCli -> id, NomCli -> nombre, etc.
            id_val = row.get('"IdCli"') or row.get('IdCli') or row.get('IdCli'.strip())
            if not id_val:
                continue
            nombre = row.get('"NomCli"') or row.get('NomCli') or ''
            organismo_id_raw = row.get('"IdOrg"') or row.get('IdOrg') or ''
            tipo_raw = row.get('"IdTipoCli"') or row.get('IdTipoCli') or '1'
            activo_raw = row.get('"CliActivo"') or row.get('CliActivo') or '1'
            
            organismo_id = int(organismo_id_raw) if organismo_id_raw else None
            tipo = int(tipo_raw) if tipo_raw else 1
            activo = 1 if activo_raw.lower() in ['true', '1', 'yes'] else 0
            
            cur.execute(
                'INSERT OR REPLACE INTO clientes (id, nombre, codigo, organismo_id, tipo_cliente, activo, creado_en) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (int(id_val), nombre.strip(), f'CLI{id_val}', organismo_id, tipo, activo, now)
            )
            count += 1
        except Exception as e:
            print(f'Error: {e} - row: {row}')
    print(f'Imported {count} clientes')

conn.commit()

# Verify
cur.execute('SELECT COUNT(*) FROM clientes')
print('Clientes in DB:', cur.fetchone()[0])
conn.close()
