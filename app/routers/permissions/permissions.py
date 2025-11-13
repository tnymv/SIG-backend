from fastapi import HTTPException, APIRouter
from app.models.permissions.permissions import Permissions
from typing import List
from datetime import datetime
from app.schemas.permissions.permissions import PermissionsBase, PermissionsResponse, PermissionsCreate, PermissionsUpdate
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.logger import create_log
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin
from app.controllers.permissions.permissions import get_all, get_by_id, create, update, toggle_state

router = APIRouter(prefix='/premissions', tags=['Permissions'])

@router.get('', response_model=List[PermissionsResponse])
async def list_permission(
    page: int = 1,
    limit: int = 10000,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        permissions, total = get_all(db, page, limit)
        total_pages = (total + limit - 1) // limit
        next_page = page + 1 if page < total_pages else None
        prev_page = page - 1 if page > 1 else None

        data = [PermissionsResponse.model_validate(emp).model_dump(mode="json") for emp in permissions]

        return success_response({
            "items": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total,
                "total_pages": total_pages,
                "next_page": next_page,
                "prev_page": prev_page
            }
        })
    except Exception as e:
        return error_response(f"Error al obtener los permisos: {e}")


@router.get('/{permission_id}', response_model=PermissionsResponse)
async def get_permissions(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)    
):
    try:
        permission = get_by_id(db, permission_id)
        return success_response(PermissionsResponse.model_validate(permission).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener el permiso {e}")

@router.post('', response_model = PermissionsResponse)
async def create_permission(
    data: PermissionsCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)  
):
    try:
        new_permission = create(db,data,current_user)
        return success_response(PermissionsResponse.model_validate(new_permission).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear el permiso: {e}")

@router.put('/{permission_id}', response_model=PermissionsResponse)
async def update_permission(
    permission_id: int,
    data: PermissionsUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)  
):
    try:
        updated_permission = update(db, permission_id, data,current_user)
        return success_response(PermissionsResponse.model_validate(updated_permission).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar el permiso {e}")

@router.delete('/{permission_id}')
async def toggle_permission_state(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)  
):
    try:
        toggle_permission = toggle_state(db, permission_id,current_user)
        action = "activo" if toggle_permission.status else "inactivo"
        return success_response({
                    "message": f"Se {action} el tipo de empleado {toggle_permission.name}, correctamente.",
                })
    except Exception as e:
        return error_response(f"Error al cambiar el estado del permiso: {e}")
