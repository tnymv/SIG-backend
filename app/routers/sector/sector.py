from app.controllers.sector.sector import get_all, get_by_id, create, update, toggle_state
from app.schemas.sector.sector import SectorResponse, SectorCreate, SectorUpdate, SectorBase
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response
from app.schemas.user.user import UserLogin
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List, Optional

router = APIRouter(prefix = '/sector', tags = ['Sector'])

@router.get('', response_model=List[SectorResponse])
async def list_sectors(
    page: int = Query(1, ge=1, description = "Número de página"),
    limit: int = Query(5, ge = 1, le=10, description="Límite de resultados por página"),
    search: Optional[str] = Query(None, description="Término de búsqueda para filtrar por nombre o descripción"),
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        sectors, total = get_all(db, page, limit, search)
        total_pages = (total + limit - 1) // limit
        next_page = page + 1 if page < total_pages else None
        prev_page = page - 1 if page > 1 else None

        data = [SectorResponse.model_validate(emp).model_dump(mode="json") for emp in sectors]

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
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/{sector_id}', response_model = SectorResponse)
async def get_sector(
    sector_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        sector = get_by_id(db, sector_id)
        return success_response(SectorResponse.model_validate(sector).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener el sector: {e}")
    
@router.post('', response_model=SectorResponse)
async def create_sector(
    data: SectorCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        sector = create(db, data, current_user)
        return success_response(SectorResponse.model_validate(sector).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear el sector: {e}")
    
@router.put('/{sector_id}', response_model=SectorResponse)
async def update_sector(
    sector_id: int,
    data: SectorUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        sector = update(db, sector_id, data, current_user)
        return success_response(SectorResponse.model_validate(sector).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar el sector: {e}")
    
@router.patch('/{sector_id}/toggle', response_model=SectorResponse)
async def toggle_sector_state(
    sector_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        toogle_sector = toggle_state(db, sector_id, current_user)
        action = "activo" if toogle_sector.active else "inactivo"
        return success_response({
            "message": f"Se {action} el sector '{toogle_sector.name}', correctamente."
        })
    except Exception as e:
        return error_response(f"Error al cambiar el estado del sector: {e}")