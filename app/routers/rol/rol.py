from app.controllers.Rol.rol import get_all, get_by_id,  create
from app.schemas.rol.rol import RolBase,RolCreate,RolResponse
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response
from app.schemas.user.user import UserLogin
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List

router = APIRouter(prefix='/rol', tags=['Rol'])

@router.get('', response_model = List[RolResponse])
async def list_rol(
    page: int = 1,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    try: 
        rol = get_all(db, page, limit)
        return success_response([RolResponse.model_validate(emp).model_dump(mode="json") for emp in rol])
    except Exception as e:
        return error_response(f"Errir al obtener los roels: {e}")

@router.get('/{id_rol}', response_model = RolResponse)
async def get_rol(
    id_rol : int,
    db: Session = Depends(get_db)
):
    try: 
        rol = get_by_id(db, id_rol)
        return success_response(RolResponse.model_validate(rol).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener el rol: {e}")

@router.post('', response_model = RolResponse)
async def create_rol(
    data: RolCreate,
    db: Session = Depends(get_db)
):
    try:
        new_rol = create(db, data)
        return success_response(RolResponse.model_validate(new_rol).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear el rol")