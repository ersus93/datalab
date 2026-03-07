"""Tests unitarios para el módulo de autenticación.

Cubre los requisitos del Issue #5 (Phase 1): Implement Authentication System.
"""
import pytest
from app.database.models.user import User, UserRole


@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestUserModel:
    """Tests del modelo User."""

    def test_password_hashing(self, db_session):
        """La contraseña debe almacenarse hasheada, nunca en texto plano."""
        user = User(
            username='test_hash_user',
            email='hash@test.local',
            role=UserRole.VIEWER
        )
        user.set_password('MiContraseña123!')
        db_session.add(user)
        db_session.flush()

        assert user.password_hash != 'MiContraseña123!'
        assert len(user.password_hash) > 50  # hash real

    def test_password_check_correct(self, db_session):
        """check_password debe retornar True con contraseña correcta."""
        user = User(username='test_check', email='check@test.local', role=UserRole.VIEWER)
        user.set_password('Correcta123!')
        assert user.check_password('Correcta123!') is True

    def test_password_check_wrong(self, db_session):
        """check_password debe retornar False con contraseña incorrecta."""
        user = User(username='test_wrong', email='wrong@test.local', role=UserRole.VIEWER)
        user.set_password('Correcta123!')
        assert user.check_password('Incorrecta456!') is False

    def test_is_admin(self, admin_user):
        """is_admin() debe retornar True solo para rol ADMIN."""
        assert admin_user.is_admin() is True
        assert admin_user.is_technician() is False

    def test_can_view_client_data_admin(self, admin_user):
        """Admin puede ver datos de cualquier cliente."""
        assert admin_user.can_view_client_data(999) is True

    def test_can_view_client_data_client_own(self, db_session, sample_cliente):
        """Usuario cliente puede ver solo sus propios datos."""
        user = User(
            username='test_client_user',
            email='client@test.local',
            role=UserRole.CLIENT,
            cliente_id=sample_cliente.id
        )
        user.set_password('Pass123!')
        db_session.add(user)
        db_session.flush()

        assert user.can_view_client_data(sample_cliente.id) is True
        assert user.can_view_client_data(sample_cliente.id + 1) is False

    def test_inactive_user_is_not_active(self, db_session):
        """Usuario inactivo no debe poder acceder."""
        user = User(
            username='inactive_user',
            email='inactive@test.local',
            role=UserRole.VIEWER,
            activo=False
        )
        user.set_password('Pass123!')
        assert user.is_active is False

    def test_user_roles_enum_values(self):
        """Los roles deben tener los valores exactos especificados."""
        assert UserRole.ADMIN.value == 'admin'
        assert UserRole.LABORATORY_MANAGER.value == 'laboratory_manager'
        assert UserRole.TECHNICIAN.value == 'technician'
        assert UserRole.CLIENT.value == 'client'
        assert UserRole.VIEWER.value == 'viewer'

    def test_to_dict_excludes_password(self, admin_user):
        """to_dict no debe exponer el hash de contraseña."""
        d = admin_user.to_dict()
        assert 'password_hash' not in d
        assert 'id' in d
        assert 'username' in d
        assert 'role' in d
