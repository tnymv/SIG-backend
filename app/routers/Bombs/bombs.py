from app.controllers.Bombs.bombs import get_all, get_by_id, create, update, toggle_state
from app.schemas.bombs.bombs import BombsResponse, BombsBase, BombsUpdate 
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response
from app.schemas.user.user import UserLogin
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List, Optional

router = APIRouter(prefix='/bombs', tags=['Bombs'])

@router.get('', response_model=List[BombsResponse])
async def list_bombs(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(5, ge=1, le=100, description="Límite de resultados por página"),
    search: Optional[str] = Query(None, description="Término de búsqueda para filtrar por nombre o conexiones"),
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
): 
    try:
        bombs, total = get_all(db, page, limit, search)
        total_pages = (total + limit - 1) // limit
        next_page = page + 1 if page < total_pages else None
        prev_page = page - 1 if page > 1 else None

        data = [BombsResponse.model_validate(emp).model_dump(mode="json") for emp in bombs]

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
    except HTTPException:
        raise
    except Exception as e:
        return error_response(f"Error al obtener las bombas: {e}")


@router.get('/{bomb_id}', response_model = BombsResponse)
async def get_bomb(
    bomb_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        bomb = get_by_id(db, bomb_id)
        return success_response(BombsResponse.model_validate(bomb).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener la bomba: {e}")

@router.post('', response_model=BombsResponse)
async def create_bomb(
    data: BombsBase,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        new_bomb = create(db, data,current_user)
        return success_response(BombsResponse.model_validate(new_bomb).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear la bomba: {e}")

@router.put('/{bomb_id}', response_model = BombsResponse)
async def update_bomb(
    bomb_id: int,
    data: BombsUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        bomb_updated = update(db, bomb_id, data,current_user)
        return success_response(BombsResponse.model_validate(bomb_updated).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar la bomba {e}")
    
@router.delete('/{bomb_id}')
async def toggle_bomb_state(
    bomb_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
): 
    try:
        toggle_bomb = toggle_state(db, bomb_id,current_user)
        action = "activo" if toggle_bomb.active else "inactivo"
        return success_response({
            "message": f"Se {action} la bomba '{toggle_bomb.name}', correctamente."
        })
    except Exception as e:
        return error_response(f"Error al cambiar el estado de la bomba: {e}")