"""add distance column to pipes

Revision ID: add_distance_pipes
Revises: 676567411805
Create Date: 2025-12-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'add_distance_pipes'
down_revision: Union[str, None] = '676567411805'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Verificar si la columna ya existe antes de agregarla
    conn = op.get_bind()
    inspector = inspect(conn)
    pipes_columns = [col['name'] for col in inspector.get_columns('pipes')]
    
    if 'distance' not in pipes_columns:
        op.add_column('pipes', sa.Column('distance', sa.Numeric(10, 3), nullable=True))


def downgrade() -> None:
    op.drop_column('pipes', 'distance')
