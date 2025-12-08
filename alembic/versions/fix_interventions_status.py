"""add missing status column to interventions

Revision ID: fix_interventions_status
Revises: add_distance_pipes
Create Date: 2025-12-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = 'fix_interventions_status'
down_revision: Union[str, None] = 'add_distance_pipes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    interventions_columns = [col['name'] for col in inspector.get_columns('interventions')]
    
    if 'status' not in interventions_columns:
        op.add_column('interventions', sa.Column('status', sa.String(20), server_default='SIN INICIAR', nullable=False))


def downgrade() -> None:
    op.drop_column('interventions', 'status')
