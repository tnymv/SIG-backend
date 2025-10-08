from fastapi import HTTPException, APIRouter
from app.models.rol.rol import Rol
from typing import List
from datetime import datetime
from app.schemas.rol.rol import RolBase, RolResponse
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin


router = APIRouter(prefix='/rol', tags=['Rol'])
    

@router.get('', response_model=List[RolResponse])
async def get_roles(
    page: int = 1, 
    limit: int = 5, 
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
    ):
    try:
            offset = (page - 1) * limit
            if page < 1 or limit < 1:
                raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
            roles = db.query(Rol).offset(offset).limit(limit).all()
            return success_response([RolResponse.model_validate(rol).model_dump(mode="json") for rol in roles])
    except Exception as e:
        return error_response(f"Error al obtener roles: {str(e)}")

@router.post('', response_model=RolResponse)
async def create_rol(
    rol_data: RolBase, 
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
    ):
    if db.query(Rol).filter(Rol.name == rol_data.name).first():
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El rol ya existe"),
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

        db.add(new_rol)
        db.commit()
        db.refresh(new_rol)
        
        
        rol_admin = db.query(Rol).filter(Rol.id_rol == 1).first()
        if rol_admin:
            rol_admin.permissions.append(new_rol)
            db.commit()

        return success_response(RolResponse.model_validate(new_rol).model_dump(mode="json"))
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al crear el rol: {str(e)}").body.decode(),
            headers={"X-Error": f"Error al crear el rol: {str(e)}"}
        )


