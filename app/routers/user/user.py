from app.controllers.User.user import get_all, get_by_id, create, update, toggle_state
from app.schemas.user.user import UserResponse, UserCreate, UserUpdate
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response
from app.schemas.user.user import UserLogin
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List

router = APIRouter(prefix='/user', tags=['User'])

@router.get('',response_model = List[UserResponse])
async def list_user(
    page: int = 1,
    limit: int = 10000, 
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try: 
        user = get_all(db, page, limit)
        return success_response([UserResponse.model_validate(emp).model_dump(mode="json") for emp in user])
    except Exception as e:
        return error_response(f"Error al obtener los usuarios: {e}")

@router.get('/{id_user}', response_model = UserResponse)
async def get_user(
    id_user: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        user = get_by_id(db, id_user)
        return success_response(UserResponse.model_validate(user).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener el usuario: {e}")

@router.post('', response_model = UserResponse)
async def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        new_user = create(db, data,current_user)
        return success_response(UserResponse.model_validate(new_user).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear el usuario: {e}")

@router.put('/{id_user}', response_model = UserResponse)
async def update_user(
    id_user: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        update_user  = update(db, id_user, data,current_user)
        return success_response(UserResponse.model_validate(update_user).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar el usuario: {e}")

@router.delete('/{id_user}')
async def toggle_user(
    id_user: int,
    db: Session = Depends (get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        toggle_user = toggle_state(db, id_user,current_user)
        action = "activo" if toggle_user.status else "inactivo"
        return success_response({
            "message": f"Se {action} el usuario {toggle_user.user}, correctamente.",
        })
    except Exception as e: 
        return error_response(f"Error al cambiar el estado del usuario: {e}")