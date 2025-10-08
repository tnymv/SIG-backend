from fastapi import HTTPException, APIRouter
from app.models.permissions.permissions import Permissions
from typing import List
from datetime import datetime
from app.schemas.permissions.permissions import PermissionsBase, PermissionsResponse
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin

router = APIRouter(prefix='/premissions', tags=['Permissions'])

@router.get('', response_model=List[PermissionsResponse]) 
async def get_permissions(
    page: int = 1, limit: int = 5,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
    ):

    try:
        offset = (page - 1) * limit
        if page < 1 or limit < 1:
         raise HTTPException(status_code=400, detail="La pagina y el limite deber ser mayores que 0")
        permissions = db.query(Permissions).offset(offset).limit(limit).all()
        return success_response([PermissionsResponse.model_validate(emp).model_dump(mode="json") for emp in permissions])
    except Exception as e:
        return error_response(f"Error al otener permisos: {str(e)}")

@router.post('', response_model=PermissionsResponse)
async def create_permissions(
    permission_data: PermissionsBase,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
    ):
    if db.query(Permissions).filter(Permissions.name == permission_data.description).first():
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El permiso ya existe"),
            headers={"X-Error": "El permiso ya existe"}
        )

    try: 
        new_permission = Permissions(
            name=permission_data.name,
            description=permission_data.description,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)

        return success_response(PermissionsResponse.model_validate(new_permission).model_dump(mode="json"))
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al crear el permiso: {str(e)}").body.decode(),
            headers={"X-Error": f"Error al crear el permiso: {str(e)}"}
        )