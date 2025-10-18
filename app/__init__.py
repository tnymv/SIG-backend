from fastapi import FastAPI, APIRouter
from starlette.responses import RedirectResponse
from app.db.database import engine, Base, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

#Aqui se importan los los schemmas
from app.controllers import rol_router,employee_router,user_router 
from app.controllers import auth_router, tank_router, report_router, permsission_router, pipes_router
from app.controllers import files_router
from app.controllers import connection_router
from app.controllers import connection_router, type_employee_router
from app.controllers import interventions_router

from app.models.user.user import Username
from app.models.employee.employee import Employee
from app.models.rol.rol import Rol
from app.models.permissions.permissions import Permissions
from app.models.type_employee.type_employees import TypeEmployee
from app.models.tanks.tanks import Tank
from app.models.pipes.pipes import Pipes  
from app.models.connection.connections import Connection

from app.models.interventions.interventions import Interventions
from app.models.intervention_entities.intervention_entities import Intervention_entities
from app.utils.auth import get_password_hash

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear todas las tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Crear Rol administrador si no existe
        admin_role = db.query(Rol).filter(Rol.name == "Administrador").first()
        if not admin_role:
            admin_role = Rol(
                name="Administrador",
                description="Rol con acceso total al sistema",
                status=1
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        # Crear TipoEmpleado "Administrador" si no existe
        admin_type_employee = db.query(TypeEmployee).filter(TypeEmployee.name == "Administrador").first()
        if not admin_type_employee:
            admin_type_employee = TypeEmployee(
                name="Administrador",
                description="Empleado con acceso completo al sistema",
                state=True
            )
            db.add(admin_type_employee)
            db.commit()
            db.refresh(admin_type_employee)

        # Crear Employee admin si no existe
        admin_employee = db.query(Employee).filter(Employee.first_name == "Admin", Employee.last_name == "Sistema").first()
        if not admin_employee:
            admin_employee = Employee(
                first_name="Admin",
                last_name="Sistema",
                phone_number="00000000",
                state=True,
                id_type_employee=admin_type_employee.id_type_employee  # asignar tipo de empleado
            )
            db.add(admin_employee)
            db.commit()
            db.refresh(admin_employee)

        # Crear Usuario admin si no existe
        admin_user = db.query(Username).filter(Username.email == "admin@sig.com").first()
        if not admin_user:
            admin_user = Username(
                user="admin",
                password_hash=get_password_hash("admin123"),
                email="admin@sig.com",
                employee_id=admin_employee.id_employee,
                rol_id=admin_role.id_rol,
                status=1
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

        permisos_por_defecto = [
            # Tuberiaas
            ('crear_tuberias', 'Puede crear registros en tuberías'),
            ('leer_tuberias', 'Puede consultar registros en tuberías'),
            ('actualizar_tuberias', 'Puede modificar registros en tuberías'),
            ('eliminar_tuberias', 'Puede eliminar registros en tuberías'),

            # Conexiones
            ('crear_conexiones', 'Puede crear registros en conexiones'),
            ('leer_conexiones', 'Puede consultar registros en conexiones'),
            ('actualizar_conexiones', 'Puede modificar registros en conexiones'),
            ('eliminar_conexiones', 'Puede eliminar registros en conexiones'),

            # Tanques
            ('crear_tanques', 'Puede crear registros en tanques'),
            ('leer_tanques', 'Puede consultar registros en tanques'),
            ('actualizar_tanques', 'Puede modificar registros en tanques'),
            ('eliminar_tanques', 'Puede eliminar registros en tanques'),

            # Desvios
            ('crear_desvios', 'Puede crear registros en desvíos'),
            ('leer_desvios', 'Puede consultar registros en desvíos'),
            ('actualizar_desvios', 'Puede modificar registros en desvíos'),
            ('eliminar_desvios', 'Puede eliminar registros en desvíos'),

            # Usuarios
            ('crear_usuarios', 'Puede crear registros en usuarios'),
            ('leer_usuarios', 'Puede consultar registros en usuarios'),
            ('actualizar_usuarios', 'Puede modificar registros en usuarios'),
            ('eliminar_usuarios', 'Puede eliminar registros en usuarios'),

            # Empleados
            ('crear_empleados', 'Puede crear registros en empleados'),
            ('leer_empleados', 'Puede consultar registros en empleados'),
            ('actualizar_empleados', 'Puede modificar registros en empleados'),
            ('eliminar_empleados', 'Puede eliminar registros en empleados'),

            # Archivos
            ('crear_archivos', 'Puede crear registros en archivos'),
            ('leer_archivos', 'Puede consultar registros en archivos'),
            ('actualizar_archivos', 'Puede modificar registros en archivos'),
            ('eliminar_archivos', 'Puede eliminar registros en archivos'),

            # Roles
            ('crear_roles', 'Puede crear registros en roles'),
            ('leer_roles', 'Puede consultar registros en roles'),
            ('actualizar_roles', 'Puede modificar registros en roles'),
            ('eliminar_roles', 'Puede eliminar registros en roles'),

            # Fontaneros
            ('crear_fontaneros', 'Puede crear registros en fontaneros'),
            ('leer_fontaneros', 'Puede consultar registros en fontaneros'),
            ('actualizar_fontaneros', 'Puede modificar registros en fontaneros'),
            ('eliminar_fontaneros', 'Puede eliminar registros en fontaneros'),

            # Intervenciones
            ('crear_intervenciones', 'Puede crear registros en intervenciones'),
            ('leer_intervenciones', 'Puede consultar registros en intervenciones'),
            ('actualizar_intervenciones', 'Puede modificar registros en intervenciones'),
            ('eliminar_intervenciones', 'Puede eliminar registros en intervenciones'),
        ]

        # Sierve para Insertar permisos si es que existen
        for nombre, descripcion in permisos_por_defecto:
            permiso_existente = db.query(Permissions).filter(Permissions.name == nombre).first()
            if not permiso_existente:
                nuevo_permiso = Permissions(
                    name=nombre,
                    description=descripcion,
                    status=True
                )
                db.add(nuevo_permiso)
        
        db.commit()
        print("Permisos por defecto creados exitosamente")

    except Exception as e:
        db.rollback()
        print(f"Error al inicializar datos: {e}")
    finally:
        db.close()
    
    yield

app = FastAPI(
    lifespan=lifespan,
    title="API SIG Backend",
    description=(
        "API para el Backend de SIG.\n\n"
        "Esta API proporciona endpoints para gestionar y acceder a las funcionalidades principales "
        "del Sistema de Información Geográfica (SIG). Incluye características para la administración "
        "de la base de datos, autenticación de usuarios, recuperación de datos e integración con otros servicios. "
        "Está diseñada para ser escalable y segura, sirviendo como la base del SIG y soportando tanto clientes internos "
        "como externos. Además, facilita la gestión eficiente de la información geoespacial, permitiendo operaciones "
        "de consulta, actualización y análisis de datos espaciales, así como la interoperabilidad con otras plataformas."
    ),
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes (para desarrollo)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite todas las cabeceras
)

api_version = APIRouter(prefix="/api/v1")

#-----
api_version.include_router(rol_router)
api_version.include_router(employee_router)
api_version.include_router(user_router)
api_version.include_router(auth_router)
api_version.include_router(tank_router)
api_version.include_router(report_router)
api_version.include_router(permsission_router)
api_version.include_router(pipes_router)
api_version.include_router(connection_router)
api_version.include_router(files_router)
api_version.include_router(type_employee_router)
api_version.include_router(interventions_router)
#-----


app.include_router(api_version)
    
@app.get('/')
async def inicio():
    return RedirectResponse(url='/docs/')