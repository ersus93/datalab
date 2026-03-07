"""Add utilizados and facturas tables

Revision ID: dd1714988574
Revises: abeec908fc2d
Create Date: 2026-03-06 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'dd1714988574'
down_revision = 'abeec908fc2d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('facturas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=True),
        sa.Column('numero_factura', sa.String(length=50), nullable=False),
        sa.Column('fecha_emision', sa.DateTime(), nullable=True),
        sa.Column('fecha_vencimiento', sa.DateTime(), nullable=True),
        sa.Column('total', sa.Numeric(precision=12, scale=2), nullable=True, default=0),
        sa.Column('estado', sa.String(length=20), nullable=True, default='BORRADOR'),
        sa.Column('creado_en', sa.DateTime(), nullable=False, default=sa.func.utcnow()),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False, default=sa.func.utcnow(), onupdate=sa.func.utcnow()),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_factura', name='uq_factura_numero')
    )
    with op.batch_alter_table('facturas', schema=None) as batch_op:
        batch_op.create_index('ix_facturas_cliente_id', ['cliente_id'], unique=False)
        batch_op.create_index('ix_facturas_estado', ['estado'], unique=False)

    op.create_table('utilizados',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entrada_id', sa.Integer(), nullable=False),
        sa.Column('detalle_ensayo_id', sa.Integer(), nullable=True),
        sa.Column('ensayo_id', sa.Integer(), nullable=False),
        sa.Column('factura_id', sa.Integer(), nullable=True),
        sa.Column('cantidad', sa.Numeric(precision=10, scale=2), nullable=True, default=1),
        sa.Column('precio_unitario', sa.Numeric(precision=12, scale=2), nullable=True, default=0),
        sa.Column('importe', sa.Numeric(precision=12, scale=2), nullable=True, default=0),
        sa.Column('fecha_uso', sa.DateTime(), nullable=True),
        sa.Column('mes_facturacion', sa.String(length=7), nullable=True),
        sa.Column('estado', sa.String(length=20), nullable=True, default='PENDIENTE'),
        sa.Column('creado_en', sa.DateTime(), nullable=False, default=sa.func.utcnow()),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False, default=sa.func.utcnow(), onupdate=sa.func.utcnow()),
        sa.ForeignKeyConstraint(['entrada_id'], ['entradas.id'], ),
        sa.ForeignKeyConstraint(['detalle_ensayo_id'], ['detalles_ensayo.id'], ),
        sa.ForeignKeyConstraint(['ensayo_id'], ['ensayos.id'], ),
        sa.ForeignKeyConstraint(['factura_id'], ['facturas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('utilizados', schema=None) as batch_op:
        batch_op.create_index('idx_utilizado_entrada_fecha', ['entrada_id', 'fecha_uso'], unique=False)
        batch_op.create_index('idx_utilizado_estado_facturacion', ['estado', 'mes_facturacion'], unique=False)
        batch_op.create_index('idx_utilizado_factura', ['factura_id'], unique=False)


def downgrade():
    with op.batch_alter_table('utilizados', schema=None) as batch_op:
        batch_op.drop_index('idx_utilizado_factura')
        batch_op.drop_index('idx_utilizado_estado_facturacion')
        batch_op.drop_index('idx_utilizado_entrada_fecha')

    op.drop_table('utilizados')

    with op.batch_alter_table('facturas', schema=None) as batch_op:
        batch_op.drop_index('ix_facturas_estado')
        batch_op.drop_index('ix_facturas_cliente_id')

    op.drop_table('facturas')
