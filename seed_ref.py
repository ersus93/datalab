import sqlite3
from datetime import datetime

conn = sqlite3.connect('instance/datalab_dev.db')
cur = conn.cursor()
now = datetime.now().isoformat()

# Insert areas
areas = [
    (1, 'Físico-Químico', 'FQ', now),
    (2, 'Microbiología', 'MB', now),
    (3, 'Evaluación Sensorial', 'ES', now),
    (4, 'Otros Servicios', 'OS', now),
]
cur.executemany('INSERT OR REPLACE INTO areas (id, nombre, sigla, creado_en) VALUES (?, ?, ?, ?)', areas)

# Insert 12 organismos
organismos = [(i+1, f'Organismo {i+1}', now) for i in range(12)]
cur.executemany('INSERT OR REPLACE INTO organismos (id, nombre, creado_en) VALUES (?, ?, ?)', organismos)

# Insert 4 provincias
provincias = [
    (1, 'Pinar del Río', 'PR', now),
    (2, 'Artemisa', 'AR', now),
    (3, 'La Habana', 'LH', now),
    (4, 'Mayabeque', 'MQ', now),
]
cur.executemany('INSERT OR REPLACE INTO provincias (id, nombre, sigla, creado_en) VALUES (?, ?, ?, ?)', provincias)

# Insert 7 destinos
destinos = [
    (1, 'Canasta Familiar', 'CF', now),
    (2, 'Amplio Consumo', 'AC', now),
    (3, 'Merienda Escolar', 'ME', now),
    (4, 'Captación Divisas', 'CD', now),
    (5, 'Destinos Especiales', 'DE', now),
    (6, 'Turismo', 'TU', now),
    (7, 'Exportación', 'EX', now),
]
cur.executemany('INSERT OR REPLACE INTO destinos (id, nombre, sigla, creado_en) VALUES (?, ?, ?, ?)', destinos)

# Insert 13 ramas
ramas = [
    (1, 'Productos Cárnicos', now),
    (2, 'Productos Lácteos', now),
    (3, 'Productos Vegetales', now),
    (4, 'Bebidas Alcohólicas', now),
    (5, 'Bebidas No Alcohólicas', now),
    (6, 'Aceites y Grasas Comestibles', now),
    (7, 'Productos de Panadería y Pastelería', now),
    (8, 'Productos de Confitería', now),
    (9, 'Productos de Molinería', now),
    (10, 'Conservas Vegetales', now),
    (11, 'Conservas Cárnicas', now),
    (12, 'Pescados y Productos del Mar', now),
    (13, 'Otros Productos Alimenticios', now),
]
cur.executemany('INSERT OR REPLACE INTO ramas (id, nombre, creado_en) VALUES (?, ?, ?)', ramas)

# Insert 12 meses
meses = [
    (1, 'Enero', 'ENE', now), (2, 'Febrero', 'FEB', now), (3, 'Marzo', 'MAR', now),
    (4, 'Abril', 'ABR', now), (5, 'Mayo', 'MAY', now), (6, 'Junio', 'JUN', now),
    (7, 'Julio', 'JUL', now), (8, 'Agosto', 'AGO', now), (9, 'Septiembre', 'SEP', now),
    (10, 'Octubre', 'OCT', now), (11, 'Noviembre', 'NOV', now), (12, 'Diciembre', 'DIC', now),
]
cur.executemany('INSERT OR REPLACE INTO meses (id, nombre, sigla, creado_en) VALUES (?, ?, ?, ?)', meses)

# Insert annos (last 5 years)
from datetime import datetime as dt
current_year = dt.now().year
annos = [(str(current_year - i), 1, now) for i in range(5)]
cur.executemany('INSERT OR REPLACE INTO annos (anno, activo, creado_en) VALUES (?, ?, ?)', annos)

conn.commit()
print('Done!')

# Verify
cur.execute('SELECT COUNT(*) FROM areas')
print('Areas:', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM organismos')
print('Organismos:', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM provincias')
print('Provincias:', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM destinos')
print('Destinos:', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM ramas')
print('Ramas:', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM meses')
print('Meses:', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM annos')
print('Annos:', cur.fetchone()[0])
conn.close()
