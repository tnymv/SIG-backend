"""Rename status and state columns to active

Revision ID: 0daef908a510
Revises: 280aed74359e
Create Date: 2025-11-24 18:13:29.033082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0daef908a510'
down_revision: Union[str, None] = '280aed74359e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Solo cambiar status y state a active, preservando datos existentes
    
    # Tablas con columna 'status'
    op.add_column('users', sa.Column('active', sa.Boolean(), nullable=True))
    op.execute("UPDATE users SET active = COALESCE(status, true)")
    op.alter_column('users', 'active', existing_type=sa.Boolean(), nullable=False)
    op.drop_column('users', 'status')
    
    op.add_column('roles', sa.Column('active', sa.Boolean(), nullable=True))
    op.execute("UPDATE roles SET active = COALESCE(status, true)")
    op.alter_column('roles', 'active', existing_type=sa.Boolean(), nullable=False)
    op.drop_column('roles', 'status')
    
    op.add_column('pipes', sa.Column('active', sa.Boolean(), nullable=True))
    op.execute("UPDATE pipes SET active = COALESCE(status, true)")
    op.alter_column('pipes', 'active', existing_type=sa.Boolean(), nullable=False)
    op.drop_column('pipes', 'status')
    
    op.add_column('permissions', sa.Column('active', sa.Boolean(), nullable=True))
    op.execute("UPDATE permissions SET active = COALESCE(status, true)")
    op.alter_column('permissions', 'active', existing_type=sa.Boolean(), nullable=False)
    op.drop_column('permissions', 'status')
    
    op.add_column('interventions', sa.Column('active', sa.Boolean(), nullable=True))
    op.execute("UPDATE interventions SET active = COALESCE(status, true)")
    op.alter_column('interventions', 'active', existing_type=sa.Boolean(), nullable=False)
    op.drop_column('interventions', 'status')
    
    op.add_column('files', sa.Column('active', sa.Boolean(), nullable=True))
    op.execute("UPDATE files SET active = COALESCE(status, true)")
    op.alter_column('files', 'active', existing_type=sa.Boolean(), nullable=False)
    op.drop_column('files', 'status')
    
    # Tablas con columna 'state'
    op.add_column('employees', sa.Column('active', sa.Boolean(), nullable=True))
    op.execute("UPDATE employees SET active = COALESCE(state, true)")
    op.alter_column('employees', 'active', existing_type=sa.Boolean(), nullable=False)
    op.drop_column('employees', 'state')
    
    op.add_column('tanks', sa.Column('active', sa.Boolean(), nullable=True))
    op.execute("UPDATE tanks SET active = COALESCE(state, true)")
    op.alter_column('tanks', 'active', existing_type=sa.Boolean(), nullable=False)
    op.drop_column('tanks', 'state')
    
    op.add_column('connections', sa.Column('active', sa.Boolean(), nullable=True))
    op.execute("UPDATE connections SET active = COALESCE(state, true)")
    op.alter_column('connections', 'active', existing_type=sa.Boolean(), nullable=False)
    op.drop_column('connections', 'state')
    
    op.add_column('type_employees', sa.Column('active', sa.Boolean(), nullable=True))
    op.execute("UPDATE type_employees SET active = COALESCE(state, true)")
    op.alter_column('type_employees', 'active', existing_type=sa.Boolean(), nullable=False)
    op.drop_column('type_employees', 'state')


def downgrade() -> None:
    # Revertir: cambiar active a status/state preservando datos
    
    # Tablas que tenían columna 'status'
    op.add_column('users', sa.Column('status', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.execute("UPDATE users SET status = COALESCE(active, true)")
    op.drop_column('users', 'active')
    
    op.add_column('roles', sa.Column('status', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.execute("UPDATE roles SET status = COALESCE(active, true)")
    op.drop_column('roles', 'active')
    
    op.add_column('pipes', sa.Column('status', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.execute("UPDATE pipes SET status = COALESCE(active, true)")
    op.drop_column('pipes', 'active')
    
    op.add_column('permissions', sa.Column('status', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.execute("UPDATE permissions SET status = COALESCE(active, true)")
    op.drop_column('permissions', 'active')
    
    op.add_column('interventions', sa.Column('status', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.execute("UPDATE interventions SET status = COALESCE(active, true)")
    op.drop_column('interventions', 'active')
    
    op.add_column('files', sa.Column('status', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.execute("UPDATE files SET status = COALESCE(active, true)")
    op.drop_column('files', 'active')
    
    # Tablas que tenían columna 'state'
    op.add_column('employees', sa.Column('state', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.execute("UPDATE employees SET state = COALESCE(active, true)")
    op.drop_column('employees', 'active')
    
    op.add_column('tanks', sa.Column('state', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.execute("UPDATE tanks SET state = COALESCE(active, true)")
    op.drop_column('tanks', 'active')
    
    op.add_column('connections', sa.Column('state', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.execute("UPDATE connections SET state = COALESCE(active, true)")
    op.drop_column('connections', 'active')
    
    op.add_column('type_employees', sa.Column('state', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.execute("UPDATE type_employees SET state = COALESCE(active, true)")
    op.drop_column('type_employees', 'active')
