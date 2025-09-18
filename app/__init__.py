from fastapi import FastAPI, APIRouter
from starlette.responses import RedirectResponse
from app.db.database import engine, Base, SessionLocal

#Aqui se importan los los schemmas
from app.controllers import rol_router,employee_router,username_router

app = FastAPI(
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

api_version = APIRouter(prefix="/api/v1")

#-----
api_version.include_router(rol_router)
api_version.include_router(employee_router)
api_version.include_router(username_router)


app.include_router(api_version)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
        
@app.on_event("shutdown")
async def shutdown():
    print("Conexión a la base de datos cerrada")
    
@app.get('/')
async def inicio():
    return RedirectResponse(url='/docs/')