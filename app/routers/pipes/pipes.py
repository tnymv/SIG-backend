from app.controllers.pipes.pipes import get_all, get_by_id, create, update, toggle_state
from app.schemas.pipes.pipes import PipesResponse,PipesResponseCreate,PipesUpdate
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response
from app.schemas.user.user import UserLogin
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List

router = APIRouter(prefix="/pipes", tags=["Pipes"])

@router.get("", response_model=List[PipesResponse])
async def list_pipes(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        pipes = get_all(db, page, limit)
        return success_response([PipesResponse.model_validate(p).model_dump(mode="json") for p in pipes])
    except Exception as e:
        return error_response(f"Error al obtener las tuberías: {e}")

@router.get("/{id_pipe}", response_model=PipesResponse)
async def get_pipe(
    id_pipe: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        pipe = get_by_id(db, id_pipe)
        return success_response(PipesResponse.model_validate(pipe).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener la tubería: {e}")

@router.post("", response_model=PipesResponse)
async def create_pipe(
    data: PipesResponseCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        new_pipe = create(db, data)
        return success_response(PipesResponse.model_validate(new_pipe).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear la tubería: {e}")

@router.put("/{id_pipe}", response_model=PipesResponse)
async def update_pipe(
    id_pipe: int,
    data: PipesUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        updated_pipe = update(db, id_pipe, data)
        return success_response(PipesResponse.model_validate(updated_pipe).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar la tubería: {e}")

@router.delete("/{id_pipe}")
async def toggle_pipe_state(
    id_pipe: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        toggle_pipe = toggle_state(db, id_pipe)
        action = "activó" if toggle_pipe.status == 1 else "inactivó"
        return success_response({
            "message": f"Se {action} la tubería {toggle_pipe.material}, correctamente.",
        })
    except Exception as e:
        return error_response(f"Error al cambiar el estado de la tubería: {e}")
