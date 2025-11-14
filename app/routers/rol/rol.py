from app.controllers.Rol.rol import get_all, get_by_id,  create
from app.schemas.rol.rol import RolBase,RolCreate,RolResponse
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response
from app.schemas.user.user import UserLogin
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List, Optional
from fastapi import HTTPException

router = APIRouter(prefix='/rol', tags=['Rol'])

@router.get('', response_model=List[RolResponse])
async def list_rol(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Límite de resultados por página"),
    search: Optional[str] = Query(None, description="Término de búsqueda para filtrar por nombre o descripción"),
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        roles, total = get_all(db, page, limit, search)
        total_pages = (total + limit - 1) // limit

        data = [RolResponse.model_validate(emp).model_dump(mode="json") for emp in roles]

        next_page = page + 1 if page < total_pages else None
        prev_page = page - 1 if page > 1 else None

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
        return error_response(f"Error al obtener los roles: {e}")


@router.get('/{id_rol}')
async def get_rol(
    id_rol : int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try: 
        rol = get_by_id(db, id_rol)
        return success_response(rol)
    except Exception as e:
        return error_response(f"Error al obtener el rol: {e}")

@router.post('', response_model = RolResponse)
async def create_rol(
    data: RolCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        new_rol = create(db, data,current_user)
        return success_response(RolResponse.model_validate(new_rol).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear el rol{e}")