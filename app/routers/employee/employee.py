from app.controllers.Employee.Emloyee import get_all,get_by_id,create,update,toggle_state
from app.schemas.employee.employee import EmployeeResponse, EmployeeCreate, EmployeeUpdate
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response
from app.schemas.user.user import UserLogin
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List

router = APIRouter(prefix='/employee', tags=['Employee'])

@router.get('',response_model=List[EmployeeResponse])
async def list_employee(
    page: int = 1,
    limit: int = 10000,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        employee = get_all(db, page, limit)
        return success_response([EmployeeResponse.model_validate(emp).model_dump(mode="json") for emp in employee])
    except Exception as e:
        return error_response(f"Error al obtener los empleados: {e}")

@router.get('/{employee_id}', response_model = EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        employee = get_by_id(db, employee_id)
        return success_response(EmployeeResponse.model_validate(employee).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener el empleado: {e}")

@router.post('',response_model=EmployeeResponse)
async def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        new_employee = create(db, data,current_user)
        return success_response(EmployeeResponse.model_validate(new_employee).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear el empleado: {e}")

@router.put('/{employee_id}', response_model = EmployeeResponse)
async def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user) 
): 
    try:
        update_employee = update(db, employee_id,data,current_user)
        return success_response(EmployeeResponse.model_validate(update_employee).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar el empleado: {e}")
    
@router.delete('/{employee_id}')
async def toggle_type_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user) 
): 
    try:
        toggle_employee = toggle_state(db, employee_id,current_user)
        action = "activo" if toggle_employee.state else "inactivo"
        return success_response({
                    "message": f"Se {action} el empleado {toggle_employee.last_name}, correctamente.",
                })
    except Exception as e:
        return error_response(f"Error al cambiar el estado del empleado: {e}")



