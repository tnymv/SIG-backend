from logging.config import fileConfig
import os
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Importar Base y modelos
from app.db.database import Base
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar todos los modelos para que Alembic los detecte
from app.models.rol.rol import Rol
from app.models.user.user import Username
from app.models.employee.employee import Employee
from app.models.tanks.tanks import Tank
from app.models.log.logs import Logs
from app.models.rol_permissions.rol_permissions import Rol_permissions
from app.models.permissions.permissions import Permissions
from app.models.connection.connections import Connection
from app.models.pipes.pipes import Pipes
from app.models.files.files import Files
from app.models.type_employee.type_employees import TypeEmployee
from app.models.interventions.interventions import Interventions
from app.models.intervention_entities.intervention_entities import Intervention_entities
from app.models.data_upload.data_upload import Data_upload
# Importar tablas de relaciones
from app.models.pipes.pipe_connections import pipe_connections
from app.models.tanks.tanks_pipes import tank_pipes

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Obtener DATABASE_URL del entorno
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Función para excluir tablas del sistema PostGIS de las migraciones autogeneradas
def include_object(object, name, type_, reflected, compare_to):
    """
    Excluir tablas del sistema PostGIS de las migraciones autogeneradas.
    """
    if type_ == "table":
        # Excluir tablas del sistema PostGIS
        if name in ('spatial_ref_sys', 'geometry_columns'):
            return False
    return True

# Función para ignorar cambios de nullable en columnas Geometry
def compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type):
    """
    Ignorar diferencias de nullable en columnas Geometry para evitar migraciones innecesarias.
    """
    from geoalchemy2 import Geometry
    
    # Si ambas columnas son Geometry, comparar solo tipo y srid, ignorando nullable
    if isinstance(inspected_type, Geometry) and isinstance(metadata_type, Geometry):
        return inspected_type.geometry_type == metadata_type.geometry_type and \
               inspected_type.srid == metadata_type.srid
    
    # Para otros tipos, usar la comparación por defecto
    return None

# Función para filtrar operaciones de alter_column que solo cambian nullable en Geometry
def process_revision_directives(context, revision, directives):
    """
    Filtrar operaciones de alter_column que solo cambian nullable o type_ en columnas Geometry.
    """
    from alembic.operations.ops import AlterColumnOp
    
    if not directives:
        return
    
    script = directives[0]
    if not hasattr(script, 'upgrade_ops') or not script.upgrade_ops:
        return
    
    # Lista de columnas Geometry que queremos proteger (tabla, columna)
    geometry_columns = [
        ('pipes', 'coordinates'),
        ('tanks', 'coordinates'),
        ('connections', 'coordenates')
    ]
    
    def filter_ops(ops_list):
        """Función recursiva para filtrar operaciones"""
        new_ops = []
        for op in ops_list:
            skip_op = False
            
            if isinstance(op, AlterColumnOp):
                # Obtener nombre de tabla y columna
                table_name = getattr(op, 'table_name', None)
                column_name = getattr(op, 'column_name', None)
                
                # Verificar si es una de las columnas Geometry protegidas
                if table_name and column_name:
                    if (table_name, column_name) in geometry_columns:
                        # Es una columna Geometry protegida - ignorar cualquier alter_column
                        skip_op = True
                
                # También verificar por el tipo si está disponible (fallback)
                if not skip_op:
                    existing_type = getattr(op, 'existing_type', None)
                    if existing_type:
                        type_str = str(existing_type)
                        if 'Geometry' in type_str or 'geometry' in type_str.lower():
                            # Para columnas Geometry, ignorar cualquier alter_column
                            skip_op = True
            
            # Si tiene operaciones anidadas (como BatchOps), filtrarlas también
            if not skip_op and hasattr(op, 'ops'):
                op.ops = filter_ops(op.ops)
            
            if not skip_op:
                new_ops.append(op)
        
        return new_ops
    
    # Filtrar operaciones recursivamente en upgrade y downgrade
    if script.upgrade_ops:
        script.upgrade_ops.ops = filter_ops(script.upgrade_ops.ops)
    if hasattr(script, 'downgrade_ops') and script.downgrade_ops:
        script.downgrade_ops.ops = filter_ops(script.downgrade_ops.ops)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=compare_type,
            compare_server_default=False,  # No comparar defaults para evitar falsos positivos
            process_revision_directives=process_revision_directives  # Filtrar operaciones innecesarias
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
