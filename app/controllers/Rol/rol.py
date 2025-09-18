from fastapi import HTTPException, APIRouter
from app.models.rol.rol import Rol
from typing import List
from datetime import datetime
from app.schemas.rol.rol import RolBase, RolCreate, RolResponse
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends


router = APIRouter(prefix='/rol', tags=['Rol']) # Define el prefijo y las etiquetas para el router
    

@router.get('', response_model=List[RolResponse])
async def get_roles(page: int = 1, limit: int = 5, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    roles = db.query(Rol).offset(offset).limit(limit).all()
    return roles

@router.post('', response_model=RolResponse)
async def create_rol(rol_data: RolBase, db: Session = Depends(get_db)):
    if db.query(Rol).filter(Rol.name == rol_data.name).first():
        raise HTTPException(
            status_code=409,
            detail="El rol ya existe",
            headers={"X-Error": "El rol ya existe"}
        )

    try:
        new_rol = Rol(
            name=rol_data.name,
            description=rol_data.description,
            status=rol_data.status,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(new_rol)   # Se agrega a la sesión
        db.commit()       # Se guardan los cambios en la BD
        db.refresh(new_rol)  # Se actualiza el objeto con los valores de la BD (id generado, etc.)

        return RolResponse.model_validate(new_rol)
    except Exception as e:
        db.rollback()  # 👈 rollback en caso de error
        raise HTTPException(
            status_code=400,
            detail=str(e),
            headers={"X-Error": str(e)}
        )

