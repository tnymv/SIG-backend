from app.controllers.interventions.interventions import get_all, get_by_id, create, update, toggle_state
from app.schemas.interventions.interventions import InterventionsResponse, InterventionsCreate, InterventionsUpdate
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response
from app.schemas.user.user import UserLogin
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List

router = APIRouter(prefix='/interventions', tags=['Interventions'])

@router.get('', response_model=List[InterventionsResponse])
async def list_interventions(
    page: int = 1,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        interventions = get_all(db, page, limit, current_user)
        return success_response(
            [InterventionsResponse.model_validate(intervention).model_dump(mode="json") for intervention in interventions],
            "Intervenciones obtenidas correctamente"
        )
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
        action = "activó" if toggle_intervention.status else "desactivó"
        return success_response(
            {"message": f"Se {action} la intervención correctamente."},
            f"Intervención {action} correctamente"
        )
    except Exception as e:
        return error_response(f"Error al cambiar el estado de la intervención: {e}")