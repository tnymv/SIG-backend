"""create bombs table and add id_bombs to intervention_entities

Revision ID: create_bombs_table
Revises: fix_interventions_status
Create Date: 2025-12-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import ARRAY
from geoalchemy2 import Geometry


revision: str = 'create_bombs_table'
down_revision: Union[str, None] = 'fix_interventions_status'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    # Crear tabla bombs si no existe
    if 'bombs' not in tables:
        op.create_table(
            'bombs',
            sa.Column('id_bombs', sa.Integer(), primary_key=True, index=True),
            sa.Column('name', sa.String(50), unique=True, index=True, nullable=False),
            sa.Column('coordinates', Geometry(geometry_type='POINT', srid=4326), nullable=True),
            sa.Column('connections', sa.String(), nullable=True),
            sa.Column('photography', ARRAY(sa.String()), nullable=True),
            sa.Column('sector_id', sa.Integer(), sa.ForeignKey('sectors.id_sector'), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('active', sa.Boolean(), default=True, nullable=False),
        )
    
    # Crear tabla de asociación bombs_pipes si no existe
    if 'bombs_pipes' not in tables:
        op.create_table(
            'bombs_pipes',
            sa.Column('bomb_id', sa.Integer(), sa.ForeignKey('bombs.id_bombs', ondelete='CASCADE'), primary_key=True),
            sa.Column('pipe_id', sa.Integer(), sa.ForeignKey('pipes.id_pipes', ondelete='CASCADE'), primary_key=True),
        )
    
    # Agregar columna id_bombs a intervention_entities si no existe
    intervention_columns = [col['name'] for col in inspector.get_columns('intervention_entities')]
    if 'id_bombs' not in intervention_columns:
        op.add_column('intervention_entities', sa.Column('id_bombs', sa.Integer(), sa.ForeignKey('bombs.id_bombs'), nullable=True))


def downgrade() -> None:
    op.drop_column('intervention_entities', 'id_bombs')
    op.drop_table('bombs_pipes')
    op.drop_table('bombs')
