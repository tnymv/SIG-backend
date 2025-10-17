from fastapi import FastAPI, APIRouter
from starlette.responses import RedirectResponse
from app.db.database import engine, Base, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

#Aqui se importan los los schemmas
from app.controllers import rol_router,employee_router,user_router 
from app.controllers import auth_router, tank_router, report_router, permsission_router, pipes_router
from app.controllers import connection_router

from app.models.user.user import Username
from app.models.employee.employee import Employee
from app.models.rol.rol import Rol
from app.utils.auth import get_password_hash

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
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

        admin_employee = db.query(Employee).filter(Employee.first_name == "Admin", Employee.last_name == "Sistema").first()
        if not admin_employee:
            admin_employee = Employee(
                first_name="Admin",
                last_name="Sistema",
                phone_number="00000000",
                state=True
            )
            db.add(admin_employee)
            db.commit()
            db.refresh(admin_employee)

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

    except Exception as e:
        db.rollback()
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
#-----


app.include_router(api_version)
    
@app.get('/')
async def inicio():
    return RedirectResponse(url='/docs/')