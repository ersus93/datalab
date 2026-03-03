# [Phase 5] Report Data Import & Validation

## Description
Import the 20 existing Informes records from the Access database and validate all report linkages, report numbers, and billing calculations. This is a critical data migration task that ensures the integrity of official laboratory reports in the new system.

## Data Context
- **Source Table**: Informes (Access)
- **Record Count**: 20 existing records
- **Dependencies**: Entradas, Detalles de Ensayos, Clientes
- **Validation Level**: Critical (legal documents)

## Requirements

### 1. Import Informes (20 Records)

**Source Schema Mapping:**
```python
INFORMES_ACCESS_SCHEMA = {
    'NroOfic': 'nro_oficial',           # Official report number
    'IdEntrada': 'entrada_id',          # FK to Entrada
    'FechaEmision': 'fecha_emision',    # Issue date
    'FechaEntrega': 'fecha_entrega',    # Delivery date
    'IdCliente': 'cliente_id',          # FK to Cliente
    'TipoInforme': 'tipo_informe',      # Report type
    'Estado': 'estado',                 # Report status
    'Observaciones': 'observaciones',   # Notes
    'EmitidoPor': 'emitido_por',        # Issuer
}
```

**Import Script:**
```python
class ImportadorInformes:
    def __init__(self, access_db_path):
        self.access = AccessConnection(access_db_path)
        self.stats = {
            'total': 0,
            'imported': 0,
            'failed': 0,
            'warnings': []
        }

    def importar(self):
        registros = self.access.query("SELECT * FROM Informes")
        self.stats['total'] = len(registros)

        for registro in registros:
            try:
                self._importar_registro(registro)
                self.stats['imported'] += 1
            except Exception as e:
                self.stats['failed'] += 1
                self.stats['warnings'].append({
                    'nro_ofic': registro.get('NroOfic'),
                    'error': str(e)
                })

        return self.stats

    def _importar_registro(self, registro):
        # Map fields
        datos = {
            'nro_oficial': registro['NroOfic'],
            'entrada_id': self._mapear_entrada(registro['IdEntrada']),
            'cliente_id': self._mapear_cliente(registro['IdCliente']),
            'fecha_emision': self._parse_fecha(registro['FechaEmision']),
            'fecha_entrega': self._parse_fecha(registro['FechaEntrega']),
            'tipo_informe': self._mapear_tipo(registro['TipoInforme']),
            'estado': self._mapear_estado(registro['Estado']),
            'observaciones': registro.get('Observaciones', ''),
        }

        # Create or update
        Informe.objects.update_or_create(
            nro_oficial=datos['nro_oficial'],
            defaults=datos
        )
```

### 2. Validate Report Linkages to Entries

**Validation Rules:**
```python
class ValidadorVinculaciones:
    def validar_todas(self):
        """Validate all report linkages"""
        resultados = {
            'ok': [],
            'errores': [],
            'advertencias': []
        }

        for informe in Informe.objects.all():
            validacion = self._validar_informe(informe)

            if validacion['nivel'] == 'OK':
                resultados['ok'].append(validacion)
            elif validacion['nivel'] == 'ERROR':
                resultados['errores'].append(validacion)
            else:
                resultados['advertencias'].append(validacion)

        return resultados

    def _validar_informe(self, informe):
        """Validate a single report"""
        errores = []
        advertencias = []

        # 1. Entry exists
        if not informe.entrada:
            errores.append("No linked to any entry")
        else:
            # 2. Entry status is compatible
            if informe.entrada.estado not in ['COMPLETADO', 'REPORTADO']:
                advertencias.append(
                    f"Entry status is {informe.entrada.estado}"
                )

            # 3. Client matches
            if informe.cliente != informe.entrada.cliente:
                errores.append(
                    f"Client mismatch: Report={informe.cliente}, "
                    f"Entry={informe.entrada.cliente}"
                )

            # 4. Report date after entry date
            if informe.fecha_emision < informe.entrada.fecha_entrada:
                errores.append(
                    f"Report date before entry date"
                )

            # 5. Tests in report belong to entry
            for detalle in informe.ensayos_incluidos.all():
                if detalle.entrada != informe.entrada:
                    errores.append(
                        f"Test {detalle.id} belongs to different entry"
                    )

        return {
            'informe': informe.nro_oficial,
            'nivel': 'ERROR' if errores else ('WARNING' if advertencias else 'OK'),
            'errores': errores,
            'advertencias': advertencias
        }
```

### 3. Verify Report Numbers

**Report Number Validation:**
```python
class ValidadorNrosOfic:
    """Validate official report numbers"""

    def verificar_duplicados(self):
        """Check for duplicate report numbers"""
        from django.db.models import Count

        duplicados = Informe.objects.values('nro_oficial').annotate(
            count=Count('id')
        ).filter(count__gt=1)

        return list(duplicados)

    def verificar_secuencia(self):
        """Check for gaps in report numbering"""
        # Extract numeric parts and check sequence
        numeros = Informe.objects.values_list('nro_oficial', flat=True)

        secuencias = {}
        for num in numeros:
            # Parse format: INF-YYYY-NNNN
            match = re.match(r'INF-(\d{4})-(\d+)', num)
            if match:
                anio, secuencia = match.groups()
                if anio not in secuencias:
                    secuencias[anio] = []
                secuencias[anio].append(int(secuencia))

        # Check for gaps
        gaps = {}
        for anio, nums in secuencias.items():
            nums.sort()
            esperado = list(range(nums[0], nums[-1] + 1))
            gaps[anio] = [n for n in esperado if n not in nums]

        return gaps

    def verificar_formato(self):
        """Check report number format"""
        invalidos = []
        formato_valido = re.compile(r'^INF-\d{4}-\d{4}$')

        for informe in Informe.objects.all():
            if not formato_valido.match(informe.nro_oficial):
                invalidos.append({
                    'nro_oficial': informe.nro_oficial,
                    'entrada': informe.entrada_id
                })

        return invalidos
```

### 4. Test Report Generation with Migrated Data

**Validation Tests:**
```python
class TestGeneracionReportesMigrados(TestCase):
    """Test report generation with migrated data"""

    def setUp(self):
        self.importador = ImportadorInformes('access_db.mdb')
        self.importador.importar()

    def test_generar_pdf_todos_los_informes(self):
        """Verify PDF generation for all migrated reports"""
        fallidos = []

        for informe in Informe.objects.all():
            try:
                pdf = generar_informe_pdf(informe.id)
                self.assertIsNotNone(pdf)
                self.assertTrue(len(pdf) > 0)
            except Exception as e:
                fallidos.append({
                    'nro_oficial': informe.nro_oficial,
                    'error': str(e)
                })

        self.assertEqual(len(fallidos), 0, f"Failed: {fallidos}")

    def test_integridad_datos_reporte(self):
        """Verify all required data is present"""
        for informe in Informe.objects.all():
            # Must have entry
            self.assertIsNotNone(informe.entrada)

            # Must have client
            self.assertIsNotNone(informe.cliente)

            # Must have tests
            self.assertTrue(informe.ensayos_incluidos.exists())

            # Must have issue date
            self.assertIsNotNone(informe.fecha_emision)

    def test_consistencia_montos(self):
        """Verify billing amounts match Access data"""
        for informe in Informe.objects.all():
            # Calculate total from linked tests
            total_calculado = sum(
                d.ensayo.precio_referencia
                for d in informe.ensayos_incluidos.all()
            )

            # Compare with Access (if stored there)
            # This would need the original Access amount
```

### 5. Validate Billing Calculations Against Access

**Billing Validation:**
```python
class ValidadorFacturacionMigrada:
    """Validate billing data migrated from Access"""

    def __init__(self, access_db_path):
        self.access = AccessConnection(access_db_path)

    def validar_calculos(self):
        """Compare calculated totals with Access"""
        discrepancias = []

        for informe in Informe.objects.all():
            # Get original Access data
            access_data = self.access.query(
                "SELECT * FROM Informes WHERE NroOfic = ?",
                (informe.nro_oficial,)
            )[0]

            # Calculate current total
            total_django = sum(
                d.ensayo.precio_referencia
                for d in informe.ensayos_incluidos.all()
            )

            # Compare with Access total (if available)
            total_access = access_data.get('MontoTotal', 0)

            if abs(total_django - total_access) > 0.01:
                discrepancias.append({
                    'nro_oficial': informe.nro_oficial,
                    'total_access': total_access,
                    'total_django': total_django,
                    'diferencia': total_django - total_access
                })

        return discrepancias

    def validar_tests_facturados(self):
        """Verify all billed tests are linked"""
        errores = []

        for informe in Informe.objects.all():
            # Get tests that should be in this report from Access
            tests_access = self.access.query(
                """SELECT IdDetalle FROM InformeDetalles
                   WHERE NroOfic = ?""",
                (informe.nro_oficial,)
            )
            access_ids = {t['IdDetalle'] for t in tests_access}

            # Get current Django tests
            django_ids = set(informe.ensayos_incluidos.values_list(
                'id_access', flat=True
            ))

            # Compare
            faltantes = access_ids - django_ids
            sobrantes = django_ids - access_ids

            if faltantes or sobrantes:
                errores.append({
                    'nro_oficial': informe.nro_oficial,
                    'faltantes': list(faltantes),
                    'sobrantes': list(sobrantes)
                })

        return errores
```

### 6. Import Validation Report

**Generate Validation Report:**
```python
def generar_reporte_validacion():
    """Generate comprehensive validation report"""

    reporte = {
        'fecha': timezone.now(),
        'resumen': {
            'total_informes': Informe.objects.count(),
            'importados_ok': 0,
            'con_errores': 0,
            'con_advertencias': 0,
        },
        'validaciones': {
            'vinculaciones': ValidadorVinculaciones().validar_todas(),
            'numeros_duplicados': ValidadorNrosOfic().verificar_duplicados(),
            'secuencia': ValidadorNrosOfic().verificar_secuencia(),
            'formato': ValidadorNrosOfic().verificar_formato(),
            'facturacion': ValidadorFacturacionMigrada().validar_calculos(),
        },
        'recomendaciones': []
    }

    # Calculate summary stats
    for v in reporte['validaciones']['vinculaciones']['ok']:
        reporte['resumen']['importados_ok'] += 1
    for v in reporte['validaciones']['vinculaciones']['errores']:
        reporte['resumen']['con_errores'] += 1
    for v in reporte['validaciones']['vinculaciones']['advertencias']:
        reporte['resumen']['con_advertencias'] += 1

    # Generate recommendations
    if reporte['validaciones']['numeros_duplicados']:
        reporte['recomendaciones'].append(
            "Resolve duplicate report numbers before go-live"
        )

    if reporte['validaciones']['facturacion']:
        reporte['recomendaciones'].append(
            "Review billing discrepancies with accounting"
        )

    return reporte
```

## Acceptance Criteria
- [ ] Import all 20 Informes records from Access
- [ ] Map and validate all foreign key relationships
- [ ] Validate report linkages to entries (100%)
- [ ] Verify report numbers (no duplicates, correct format)
- [ ] Test PDF generation with migrated data
- [ ] Validate billing calculations against Access
- [ ] Generate validation report with discrepancies
- [ ] Document any data issues found
- [ ] Obtain stakeholder sign-off on migrated data
- [ ] Create rollback procedure

## Technical Notes
- Run import in a transaction (rollback on error)
- Log all validation errors for review
- Create data correction scripts for common issues
- Backup before running import
- Test import on staging environment first
- Maintain Access record IDs for traceability
- Generate reconciliation report for accounting
- Consider manual review for critical reports

## Labels
`phase-5`, `data-migration`, `import`, `validation`, `reports`, `billing`, `backend`

## Estimated Effort
**Story Points**: 5
**Time Estimate**: 2-3 days
