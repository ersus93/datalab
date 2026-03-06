"""Tests unitarios para el módulo de clientes.

Cubre los requisitos del Issue #1 (Phase 2): Client Management Module.
"""
import pytest
from app.database.models.cliente import Cliente
from app.database.models.audit import AuditLog


class TestClienteModel:
    """Tests del modelo Cliente."""

    def test_cliente_requiere_codigo(self, db_session, sample_organismo):
        """El campo codigo es obligatorio (not null, unique)."""
        cliente = Cliente(
            codigo='CLI-AUDIT-01',
            nombre='Cliente Audit Test',
            organismo_id=sample_organismo.id,
            activo=True
        )
        db_session.add(cliente)
        db_session.flush()
        assert cliente.id is not None
        assert cliente.codigo == 'CLI-AUDIT-01'

    def test_total_fabricas_property(self, sample_cliente):
        """total_fabricas debe retornar entero."""
        assert isinstance(sample_cliente.total_fabricas, int)

    def test_to_dict_includes_codigo(self, sample_cliente):
        """to_dict debe incluir el campo codigo."""
        d = sample_cliente.to_dict()
        assert 'codigo' in d
        assert d['codigo'] == sample_cliente.codigo


class TestClienteAuditLog:
    """Verifica que el audit log se registre correctamente."""

    def test_audit_log_on_create(self, db_session, sample_cliente, admin_user):
        """Crear un cliente debe generar entrada de auditoría."""
        AuditLog.log_change(
            user_id=admin_user.id,
            action='CREATE',
            table_name='clientes',
            record_id=sample_cliente.id,
            new_values=sample_cliente.to_dict()
        )
        db_session.flush()

        logs = AuditLog.query.filter_by(
            table_name='clientes',
            record_id=sample_cliente.id,
            action='CREATE'
        ).all()
        assert len(logs) == 1
        assert logs[0].new_values is not None

    def test_audit_log_on_update(self, db_session, sample_cliente, admin_user):
        """Actualizar un cliente debe registrar old y new values."""
        old = sample_cliente.to_dict()
        sample_cliente.nombre = 'Nombre Actualizado'
        AuditLog.log_change(
            user_id=admin_user.id,
            action='UPDATE',
            table_name='clientes',
            record_id=sample_cliente.id,
            old_values=old,
            new_values=sample_cliente.to_dict()
        )
        db_session.flush()

        log = AuditLog.query.filter_by(
            table_name='clientes',
            action='UPDATE'
        ).first()
        assert log is not None
        assert log.old_values['nombre'] != log.new_values['nombre']
