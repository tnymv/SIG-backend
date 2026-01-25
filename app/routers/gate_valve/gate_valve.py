from app.controllers.gate_valve.gate_valve import get_all, get_by_id, create, update, toggle_state
from app.schemas.gate_valve.gate_valve import Gate_valveResponse, Gate_valveCreate, Gate_valveUpdate 
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response
from app.schemas.user.user import UserLogin
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List, Optional

router = APIRouter(prefix='/gate_valve', tags=['Gate Valve'])

@router.get('', response_model=List[Gate_valveResponse])
async def list_valves(
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
): 
    try:
        valves, total = get_all(db, page, limit, search)
        total_pages = (total + limit - 1) // limit
        
        data = [Gate_valveResponse.model_validate(v).model_dump(mode="json") for v in valves]

        return success_response({
            "items": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total,
                "total_pages": total_pages,
                "next_page": page + 1 if page < total_pages else None,
                "prev_page": page - 1 if page > 1 else None
            }
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        return error_response(f"Error al obtener las válvulas: {e}")

@router.get('/{valve_id}', response_model=Gate_valveResponse)
async def get_valve(
    valve_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        valve = get_by_id(db, valve_id)
        return success_response(Gate_valveResponse.model_validate(valve).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener la válvula: {e}")

@router.post('', response_model=Gate_valveResponse)
async def create_gate_valve(
    data: Gate_valveCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        new_valve = create(db, data, current_user)
        return success_response(Gate_valveResponse.model_validate(new_valve).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear la válvula: {e}")

@router.put('/{valve_id}', response_model=Gate_valveResponse)
async def update_gate_valve(
    valve_id: int,
    data: Gate_valveUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        updated = update(db, valve_id, data, current_user)
        return success_response(Gate_valveResponse.model_validate(updated).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar la válvula: {e}")

@router.delete('/{valve_id}')
async def toggle_gate_valve_state(
    valve_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
): 
    try:
        valve = toggle_state(db, valve_id, current_user)
        action = "activó" if valve.active else "desactivó"
        return success_response({
            "message": f"Se {action} la válvula '{valve.name}' correctamente."
        })
    except Exception as e:
        return error_response(f"Error al cambiar el estado: {e}")