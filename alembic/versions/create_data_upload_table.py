"""create data_upload table

Revision ID: create_data_upload
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_data_upload'
down_revision = 'bbed30f095c2'  # Última migración: add_status_to_interventions
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Verificar si la tabla ya existe antes de crearla
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    if 'data_upload' not in tables:
        # Crear tabla data_upload
        op.create_table(
            'data_upload',
            sa.Column('siaf', sa.String(length=100), nullable=False),
            sa.Column('institutional_classification', sa.Integer(), nullable=False),
            sa.Column('report', sa.String(length=200), nullable=False),
            sa.Column('date', sa.DateTime(), nullable=False),
            sa.Column('hour', sa.Time(), nullable=False),
            sa.Column('seriereport', sa.String(length=100), nullable=False),
            sa.Column('user', sa.String(length=100), nullable=False),
            sa.Column('identifier', sa.String(length=100), nullable=False, primary_key=True),
            sa.Column('taxpayer', sa.String(length=100), nullable=False),
            sa.Column('cologne', sa.String(length=200), nullable=False),
            sa.Column('cat_service', sa.String(length=250), nullable=False),
            sa.Column('cannon', sa.Float(), nullable=False),
            sa.Column('excess', sa.Float(), nullable=False),
            sa.Column('total', sa.Float(), nullable=False),
            sa.Column('status', sa.Boolean(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
        )
        
        # Crear índices solo si la tabla se creó
        op.create_index(op.f('ix_data_upload_siaf'), 'data_upload', ['siaf'], unique=False)
        op.create_index(op.f('ix_data_upload_institutional_classification'), 'data_upload', ['institutional_classification'], unique=False)
        op.create_index(op.f('ix_data_upload_report'), 'data_upload', ['report'], unique=False)
        op.create_index(op.f('ix_data_upload_date'), 'data_upload', ['date'], unique=False)
        op.create_index(op.f('ix_data_upload_hour'), 'data_upload', ['hour'], unique=False)
        op.create_index(op.f('ix_data_upload_seriereport'), 'data_upload', ['seriereport'], unique=False)
        op.create_index(op.f('ix_data_upload_user'), 'data_upload', ['user'], unique=False)
        op.create_index(op.f('ix_data_upload_identifier'), 'data_upload', ['identifier'], unique=True)
        op.create_index(op.f('ix_data_upload_taxpayer'), 'data_upload', ['taxpayer'], unique=False)
        op.create_index(op.f('ix_data_upload_cologne'), 'data_upload', ['cologne'], unique=False)
        op.create_index(op.f('ix_data_upload_cat_service'), 'data_upload', ['cat_service'], unique=False)
        op.create_index(op.f('ix_data_upload_cannon'), 'data_upload', ['cannon'], unique=False)
        op.create_index(op.f('ix_data_upload_excess'), 'data_upload', ['excess'], unique=False)
        op.create_index(op.f('ix_data_upload_total'), 'data_upload', ['total'], unique=False)
        op.create_index(op.f('ix_data_upload_status'), 'data_upload', ['status'], unique=False)


def downgrade() -> None:
    # Eliminar índices
    op.drop_index(op.f('ix_data_upload_status'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_total'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_excess'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_cannon'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_cat_service'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_cologne'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_taxpayer'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_identifier'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_user'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_seriereport'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_hour'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_date'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_report'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_institutional_classification'), table_name='data_upload')
    op.drop_index(op.f('ix_data_upload_siaf'), table_name='data_upload')
    
    # Eliminar tabla
    op.drop_table('data_upload')

