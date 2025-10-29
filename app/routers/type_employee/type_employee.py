from app.controllers.type_employee.type_employees import get_all, get_by_id, create, update, toggle_state
from app.schemas.type_employee.type_employees import TypeEmployeeResponse, TypeEmployeeCreate, TypeEmployeeUpdate
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response
from app.schemas.user.user import UserLogin
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List

router = APIRouter(prefix='/type_employee', tags=['Type Employee'])

@router.get('', response_model = List[TypeEmployeeResponse])
async def list_type_employees(
    page: int = 1,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        type_employee = get_all(db, page, limit)
        return success_response([TypeEmployeeResponse.model_validate(emp).model_dump(mode="json") for emp in type_employee])
    except Exception as e:
        return error_response(f"Error al obtener los tipos de empleados: {e}")

@router.get('/{id_type_employee}', response_model = TypeEmployeeResponse)
async def get_type_employee(
    id_type_employee: int, 
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
): 
    try:
        type_employee = get_by_id(db, id_type_employee)
        return success_response(TypeEmployeeResponse.model_validate(type_employee).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener el tipo de empleado: {e}")
    
@router.post('', response_model = TypeEmployeeResponse)
async def create_type_employee(
    data: TypeEmployeeCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        new_type_employee = create(db, data)
        return success_response(TypeEmployeeResponse.model_validate(new_type_employee).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear el tipo de empleado: {e}")
    
@router.put('/{id_type_employee}', response_model = TypeEmployeeResponse)
async def update_type_employee(
    id_type_employee: int, 
    data: TypeEmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        updated_type_employee = update(db, id_type_employee,data)
        return success_response(TypeEmployeeResponse.model_validate(updated_type_employee).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar el tipo de empleado: {e}")

@router.delete('/{id_type_employee}')
async def toggle_type_employee_state(
    id_type_employee: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        toggle_type_employee = toggle_state(db, id_type_employee)
        action = "activo" if toggle_type_employee.state else "inactivo"
        return success_response({
                    "message": f"Se {action} el tipo de empleado {toggle_type_employee.id_type_employee}, correctamente.",
                })
    except Exception as e:
        return error_response(f"Error al cambiar el estado del tipo de empleado: {e}")