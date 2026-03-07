"""Script de importación con mapeo de columnas CSV a campos de modelo.
Mapea las columnas del CSV (IdCli, NomCli, etc.) a los campos del modelo (id, nombre, etc.)
"""
import os
import sys
os.chdir('C:/Users/ernes/datalab')
sys.path.insert(0, 'C:/Users/ernes/datalab')

import csv
from datetime import datetime
from app import create_app, db
from app.database.models import Cliente, Fabrica, Producto, Ensayo, Entrada
from app.database.models.detalle_ensayo import DetalleEnsayo
from app.database.models.utilizado import Utilizado

app = create_app('development')

def clean_int(val):
    if val is None or val == '' or val == 'None':
        return None
    try:
        return int(val)
    except:
        return None

def clean_bool(val):
    if val is None or val == '' or val == 'None':
        return 1
    return 1 if str(val).lower() in ['true', '1', 'yes'] else 0

def clean_float(val):
    if val is None or val == '' or val == 'None':
        return None
    try:
        return float(str(val).replace(',', '.'))
    except:
        return None

with app.app_context():
    print("=== Importando clientes ===")
    with open('data/migrations/clientes.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                cliente = Cliente(
                    id=clean_int(row.get('IdCli')),
                    nombre=row.get('NomCli', '').strip(),
                    codigo=f"CLI{row.get('IdCli', '')}",
                    organismo_id=clean_int(row.get('IdOrg')),
                    tipo_cliente=clean_int(row.get('IdTipoCli')) or 1,
                    activo=clean_bool(row.get('CliActivo'))
                )
                db.session.merge(cliente)
                count += 1
            except Exception as e:
                print(f"Error: {e}")
        db.session.commit()
        print(f"   Importados: {count}")
    
    print("\n=== Importando fabricas ===")
    with open('data/migrations/fabricas.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                fabrica = Fabrica(
                    id=clean_int(row.get('IdFca')),
                    nombre=row.get('NomFca', '').strip(),
                    cliente_id=clean_int(row.get('IdCli')),
                    provincia_id=clean_int(row.get('IdPro')),
                    activo=1
                )
                db.session.merge(fabrica)
                count += 1
            except Exception as e:
                print(f"Error: {e}")
        db.session.commit()
        print(f"   Importados: {count}")
    
    print("\n=== Importando productos ===")
    with open('data/migrations/productos.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                producto = Producto(
                    id=clean_int(row.get('IdPro')),
                    nombre=row.get('NomPro', '').strip(),
                    destino_id=clean_int(row.get('IdDest')),
                    rama_id=clean_int(row.get('IdRama')),
                    activo=clean_bool(row.get('ProActivo'))
                )
                db.session.merge(producto)
                count += 1
            except Exception as e:
                print(f"Error: {e}")
        db.session.commit()
        print(f"   Importados: {count}")
    
    print("\n=== Importando ensayos ===")
    with open('data/migrations/ensayos.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                area_id = clean_int(row.get('IdArea'))
                if area_id is None:
                    # Map area from code
                    codigo = row.get('CodEnsayo', '')
                    if codigo.startswith('FQ'):
                        area_id = 1
                    elif codigo.startswith('MB'):
                        area_id = 2
                    elif codigo.startswith('ES'):
                        area_id = 3
                    else:
                        area_id = 4
                
                ensayo = Ensayo(
                    id=clean_int(row.get('IdEnsayo')),
                    nombre_corto=row.get('NomEnsayo', '').strip(),
                    nombre_oficial=row.get('NomEnsayo', '').strip(),
                    area_id=area_id,
                    precio=clean_float(row.get('Precio', 0)) or 0,
                    activo=1
                )
                db.session.merge(ensayo)
                count += 1
            except Exception as e:
                print(f"Error: {e}")
        db.session.commit()
        print(f"   Importados: {count}")
    
    print("\n=== Importando entradas ===")
    with open('data/migrations/entradas.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                entrada = Entrada(
                    id=clean_int(row.get('IdEntrada')),
                    producto_id=clean_int(row.get('IdPro')),
                    fabrica_id=clean_int(row.get('IdFca')),
                    cliente_id=clean_int(row.get('IdCli')),
                    codigo=f"ENT{row.get('IdEntrada', '')}",
                    cantidad_recib=clean_int(row.get('CantRecib')) or 0,
                    cantidad_muest=clean_int(row.get('CantMuest')) or 0,
                    status=row.get('Status', 'RECIBIDA')
                )
                db.session.merge(entrada)
                count += 1
            except Exception as e:
                print(f"Error: {e}")
        db.session.commit()
        print(f"   Importados: {count}")
    
    print("\n=== Importando detalles_ensayo ===")
    with open('data/migrations/detalles_ensayos.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                detalle = DetalleEnsayo(
                    id=clean_int(row.get('IdDetalle')),
                    entrada_id=clean_int(row.get('IdEntrada')),
                    ensayo_id=clean_int(row.get('IdEnsayo')),
                    cantidad=clean_int(row.get('Cantidad', 1)) or 1,
                    estado='COMPLETADO'  # Historical data
                )
                db.session.merge(detalle)
                count += 1
            except Exception as e:
                print(f"Error: {e}")
        db.session.commit()
        print(f"   Importados: {count}")
    
    print("\n=== Importando utilizados ===")
    with open('data/migrations/utilizado_r.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                utilizado = Utilizado(
                    id=clean_int(row.get('IdUtilizado')),
                    entrada_id=clean_int(row.get('IdEntrada')),
                    ensayo_id=clean_int(row.get('IdEnsayo')),
                    cantidad=clean_float(row.get('Cantidad', 1)) or 1,
                    precio_unitario=clean_float(row.get('Precio', 0)) or 0,
                    importe=clean_float(row.get('Importe', 0)) or 0,
                    estado='PENDIENTE'
                )
                db.session.merge(utilizado)
                count += 1
            except Exception as e:
                print(f"Error: {e}")
        db.session.commit()
        print(f"   Importados: {count}")
    
    # Verificar
    print("\n=== Verificación ===")
    print(f"Clientes: {Cliente.query.count()}")
    print(f"Fabricas: {Fabrica.query.count()}")
    print(f"Productos: {Producto.query.count()}")
    print(f"Ensayos: {Ensayo.query.count()}")
    print(f"Entradas: {Entrada.query.count()}")
    print(f"Detalles Ensayo: {DetalleEnsayo.query.count()}")
    print(f"Utilizados: {Utilizado.query.count()}")
    print("\n=== Completado ===")
