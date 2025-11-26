from app.controllers.interventions.interventions import get_all, get_by_id, create, update, toggle_state
from app.schemas.interventions.interventions import InterventionsResponse, InterventionsCreate, InterventionsUpdate, InterventionStatus
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response
from app.schemas.user.user import UserLogin
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List, Optional

router = APIRouter(prefix='/interventions', tags=['Interventions'])

@router.get('', response_model=List[InterventionsResponse])
async def list_interventions(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10000, ge=1, le=10000, description="Límite de resultados por página"),
    search: Optional[str] = Query(None, description="Término de búsqueda para filtrar por descripción"),
    status: Optional[InterventionStatus] = Query(None, description="Filtrar por estado: SIN INICIAR, EN CURSO, FINALIZADO"),
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        # Convertir el enum a string para pasarlo al controlador
        status_str = status.value if status else None
        interventions, total = get_all(db, page, limit, search, status_str)
        total_pages = (total + limit - 1) // limit
        next_page = page + 1 if page < total_pages else None
        prev_page = page - 1 if page > 1 else None

        data = [InterventionsResponse.model_validate(i).model_dump(mode="json") for i in interventions]

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
        }, "Intervenciones obtenidas correctamente")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(f"Error al obtener las intervenciones: {e}")


@router.get('/{intervention_id}', response_model=InterventionsResponse)
async def get_intervention(
    intervention_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        intervention = get_by_id(db, intervention_id)
        return success_response(
            InterventionsResponse.model_validate(intervention).model_dump(mode="json"),
            "Intervención obtenida correctamente"
        )
    except Exception as e:
        return error_response(f"Error al obtener la intervención: {e}")

@router.post('', response_model=InterventionsResponse)
async def create_intervention(
    data: InterventionsCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        new_intervention = create(db, data, current_user)
        return success_response(
            InterventionsResponse.model_validate(new_intervention).model_dump(mode="json"),
            "Intervención creada correctamente"
        )
    except Exception as e:
        return error_response(f"Error al crear la intervención: {e}")

@router.put('/{intervention_id}', response_model=InterventionsResponse)
async def update_intervention(
    intervention_id: int,
    data: InterventionsUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        updated_intervention = update(db, intervention_id, data, current_user)
        return success_response(
            InterventionsResponse.model_validate(updated_intervention).model_dump(mode="json"),
            "Intervención actualizada correctamente"
        )
    except Exception as e:
        return error_response(f"Error al actualizar la intervención: {e}")

@router.delete('/{intervention_id}')
async def toggle_intervention_state(
    intervention_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        toggle_intervention = toggle_state(db, intervention_id, current_user)
        action = "activó" if toggle_intervention.active else "desactivó"
        return success_response(
            {"message": f"Se {action} la intervención correctamente."},
            f"Intervención {action} correctamente"
        )
    except Exception as e:
        return error_response(f"Error al cambiar el estado de la intervención: {e}")