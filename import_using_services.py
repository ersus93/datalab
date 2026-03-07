"""Script de importación usando los servicios de Flask.
Utiliza los servicios existentes de la app para importar datos correctamente.
"""
import os
import sys
os.chdir('C:/Users/ernes/datalab')
sys.path.insert(0, 'C:/Users/ernes/datalab')

from app import create_app, db
from app.services.import_service import MasterDataImportService

app = create_app('development')

with app.app_context():
    print("=== Importando datos usando servicios Flask ===\n")
    
    # Importar clientes
    print("1. Importando clientes...")
    service = MasterDataImportService(dry_run=False)
    result = service.import_clientes('data/migrations/clientes.csv', skip_existing=False)
    print(f"   Clientes importados: {result.imported}")
    print(f"   Errores: {len(result.errors)}")
    if result.errors:
        for e in result.errors[:3]:
            print(f"   - {e.message}")
    
    db.session.commit()
    
    # Importar fabricas
    print("\n2. Importando fabricas...")
    result = service.import_fabricas('data/migrations/fabricas.csv', skip_existing=False)
    print(f"   Fabricas importadas: {result.imported}")
    print(f"   Errores: {len(result.errors)}")
    
    db.session.commit()
    
    # Importar productos
    print("\n3. Importando productos...")
    result = service.import_productos('data/migrations/productos.csv', skip_existing=False)
    print(f"   Productos importados: {result.imported}")
    print(f"   Errores: {len(result.errors)}")
    
    db.session.commit()
    
    # Verificar
    print("\n=== Verificación ===")
    from app.database.models import Cliente, Fabrica, Producto, Area, Organismo
    from app.database.models import Ensayo, Entrada
    from app.database.models.detalle_ensayo import DetalleEnsayo
    from app.database.models.utilizado import Utilizado
    
    print(f"Clientes: {Cliente.query.count()}")
    print(f"Fabricas: {Fabrica.query.count()}")
    print(f"Productos: {Producto.query.count()}")
    print(f"Areas: {Area.query.count()}")
    print(f"Organismos: {Organismo.query.count()}")
    print(f"Ensayos: {Ensayo.query.count()}")
    print(f"Entradas: {Entrada.query.count()}")
    print(f"Detalles Ensayo: {DetalleEnsayo.query.count()}")
    print(f"Utilizados: {Utilizado.query.count()}")
    
    print("\n=== Importación completada ===")
