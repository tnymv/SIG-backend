from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.controllers.assigments.assignments import (
    get_all,
    get_by_id,
    create,
    update,
    toggle_state
)

from app.schemas.assignments.assignments import (
    AssignmentResponse,
    AssignmentCreate,
    AssignmentUpdate
)

from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin
from app.utils.response import success_response, error_response
from app.db.database import get_db


router = APIRouter(prefix="/assignments", tags=["Assignments"])

@router.get("", response_model=List[AssignmentResponse])
async def list_assignments(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(5, ge=1, le=10, description="Límite de resultados por página"),
    search: Optional[str] = Query(None, description="Buscar por estado o notas"),
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        assignments, total = get_all(db, page, limit, search)
        total_pages = (total + limit - 1) // limit

        next_page = page + 1 if page < total_pages else None
        prev_page = page - 1 if page > 1 else None

        data = [AssignmentResponse.model_validate(a).model_dump(mode="json") for a in assignments]

        return success_response({
            "items": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total,
                "total_pages": total_pages,
                "next_page": next_page,
                "prev_page": prev_page,
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        assignment = get_by_id(db, assignment_id)
        return success_response(AssignmentResponse.model_validate(assignment).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener la asignación: {e}")

@router.post("", response_model=AssignmentResponse)
async def create_assignment(
    data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        assignment = create(db, data, current_user)
        return success_response(AssignmentResponse.model_validate(assignment).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear la asignación: {e}")

@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    data: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        updated_assignment = update(db, assignment_id, data, current_user)
        return success_response(AssignmentResponse.model_validate(updated_assignment).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar la asignación: {e}")

@router.patch("/{assignment_id}/toggle", response_model=AssignmentResponse)
async def toggle_assignment_state(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        toggled = toggle_state(db, assignment_id, current_user)
        action = "activo" if toggled.active else "inactivo"

        return success_response({
            "message": f"Se cambió el estado de la asignación {toggled.id_assignment} a {action}.",
            "id_assignment": toggled.id_assignment
        })
    except Exception as e:
        return error_response(f"Error al cambiar el estado de la asignación: {e}")
