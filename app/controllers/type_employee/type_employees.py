from app.schemas.type_employee.type_employees import TypeEmployeeBase,TypeEmployeeResponse,TypeEmployeeUpdate
from app.utils.response import success_response, error_response, existence_response_dict
from app.controllers.auth.auth_controller import get_current_active_user
from app.models.type_employee.type_employees import TypeEmployee
from fastapi import HTTPException, APIRouter, Depends
from app.schemas.user.user import UserLogin
from app.db.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime 
from typing import List

router = APIRouter(prefix='/type_employee', tags=['Type Employee'])

@router.get('', response_model=List[TypeEmployeeResponse])
async def get_type_employees(
    page: int = 1, limit: int = 5, 
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        offset = (page - 1) * limit
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
        type_employees = db.query(TypeEmployee).offset(offset).limit(limit).all()
        return success_response([TypeEmployeeResponse.model_validate(emp).model_dump(mode="json") for emp in type_employees])
    except Exception as e:
        return error_response(f"Error al obtener empleados: {str(e)}")

@router.post('', response_model=TypeEmployeeResponse)
async def create_type_employee(
    type_employee_data: TypeEmployeeBase, 
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    if db.query(TypeEmployee).filter(TypeEmployee.name == type_employee_data.name).first():
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El tipo de empleado ya existe"),
            headers={"X-Error": "El tipo de empleado ya existe"}
        )

    try:
        new_type_employee = TypeEmployee(
            name=type_employee_data.name,
            description=type_employee_data.description,
            state=type_employee_data.state,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(new_type_employee)
        db.commit()
        db.refresh(new_type_employee)
        return success_response(TypeEmployeeResponse.model_validate(new_type_employee).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear el tipo de empleado: {str(e)}")
    
@router.put('/{type_employee_id}', response_model=TypeEmployeeResponse)
async def update_type_employee(
    type_employee_id: int,
    type_employee_data: TypeEmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    type_employee = db.query(TypeEmployee).filter(TypeEmployee.id_type_employee == type_employee_id).first()
    if not type_employee:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El tipo de empleado no existe"),
            headers={"X-Error": "El tipo de empleado no existe"}
        )

    try:
        if type_employee_data.name is not None:
            type_employee.name = type_employee_data.name
        if type_employee_data.description is not None:
            type_employee.description = type_employee_data.description
        if type_employee_data.state is not None:
            type_employee.state = type_employee_data.state
        type_employee.updated_at = datetime.now()

        db.commit()
        db.refresh(type_employee)
        return success_response(TypeEmployeeResponse.model_validate(type_employee).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar el tipo de empleado: {str(e)}")
    
@router.get('/{type_employee_id}', response_model=TypeEmployeeResponse)
async def get_type_employee(
    type_employee_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    type_employee = db.query(TypeEmployee).filter(TypeEmployee.id_type_employee == type_employee_id).first()
    if not type_employee:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El tipo de empleado no existe"),
            headers={"X-Error": "El tipo de empleado no existe"}
        )
    try:
        return success_response(TypeEmployeeResponse.model_validate(type_employee).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener el tipo de empleado: {str(e)}")

@router.delete('/{type_employee_id}')
async def delete_type_employee(
    type_employee_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    type_employee = db.query(TypeEmployee).filter(TypeEmployee.id_type_employee == type_employee_id).first()
    if not type_employee:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El tipo de empleado no existe"),
            headers={"X-Error": "El tipo de empleado no existe"}
        )
    try:
        new_state = not type_employee.state
        type_employee.state = new_state
        type_employee.updated_at = datetime.now()
        db.commit()
        db.refresh(type_employee)
        
        action_text = "activó" if new_state else "desactivó"
        return success_response({
            "message": f"Se ha {action_text} el tipo de empleado correctamente.",
        })
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al desactivar el empleado: {str(e)}").body.decode(),
            headers={"X-Error": f"Error al desactivar el empleado: {str(e)}"}
        )