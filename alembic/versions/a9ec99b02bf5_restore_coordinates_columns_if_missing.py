"""Restore coordinates columns if missing

Revision ID: a9ec99b02bf5
Revises: 0daef908a510
Create Date: 2025-11-24 18:52:22.129147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision: str = 'a9ec99b02bf5'
down_revision: Union[str, None] = '0daef908a510'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Restaurar columnas de coordenadas SOLO si no existen.
    Esta migración NO inicializa valores por defecto para preservar datos existentes.
    Si las columnas ya existían antes, los datos deberían restaurarse desde backup.
    """
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    def table_exists(table_name):
        """Verifica si una tabla existe"""
        return table_name in inspector.get_table_names()
    
    # Restaurar columna coordinates en pipes (LINESTRING)
    if table_exists('pipes'):
        pipes_columns = [col['name'] for col in inspector.get_columns('pipes')]
        if 'coordinates' not in pipes_columns:
            # Agregar como nullable para no perder datos existentes
            op.add_column('pipes', sa.Column('coordinates', Geometry(geometry_type='LINESTRING', srid=4326), nullable=True))
            # NO inicializamos valores por defecto - los datos deben venir de backup si existían
    
    # Restaurar columna coordinates en tanks (POINT)
    if table_exists('tanks'):
        tanks_columns = [col['name'] for col in inspector.get_columns('tanks')]
        if 'coordinates' not in tanks_columns:
            # Agregar como nullable para no perder datos existentes
            op.add_column('tanks', sa.Column('coordinates', Geometry(geometry_type='POINT', srid=4326), nullable=True))
            # NO inicializamos valores por defecto - los datos deben venir de backup si existían
    
    # Restaurar columna coordenates en connections (POINT) - nota: el modelo usa 'coordenates' con 'e'
    if table_exists('connections'):
        connections_columns = [col['name'] for col in inspector.get_columns('connections')]
        if 'coordenates' not in connections_columns:
            # Agregar como nullable para no perder datos existentes
            op.add_column('connections', sa.Column('coordenates', Geometry(geometry_type='POINT', srid=4326), nullable=True))
            # NO inicializamos valores por defecto - los datos deben venir de backup si existían


def downgrade() -> None:
    """
    NO eliminar las columnas en downgrade para preservar datos.
    Si necesitas eliminar las columnas, hazlo manualmente después de restaurar desde backup.
    """
    # Intencionalmente vacío - NO eliminamos las columnas para preservar datos
    pass
