from fastapi import HTTPException, APIRouter
from app.models.employee.employee import Employee
from typing import List
from datetime import datetime
from app.schemas.employee.employee import EmployeeBase, EmployeeResponse, EmployeeUpdate
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.logger import create_log
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin
from app.models.type_employee.type_employees import TypeEmployee

router = APIRouter(prefix='/employee', tags=['Employee'])

@router.get('', response_model=List[EmployeeResponse])
async def get_employees(
    page: int = 1, limit: int = 5, 
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
        offset = (page - 1) * limit
        employees = db.query(Employee).offset(offset).limit(limit).all()
        
        create_log(
            db,
            user_id=current_user.id_user,
            action="READ",
            entity="Employee",
            description=f"El usuario {current_user.user} accedió a la lista de empleados"
        )
        
        return success_response([EmployeeResponse.model_validate(emp).model_dump(mode="json") for emp in employees])
    except Exception as e:
        return error_response(f"Error al obtener empleados: {str(e)}")


@router.post('', response_model=EmployeeResponse)
async def create_employee(
    employee_data: EmployeeBase, 
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    type_emp = db.query(TypeEmployee).filter(TypeEmployee.id_type_employee == employee_data.id_type_employee).first()
    if not type_emp:
        raise HTTPException(
            status_code=404,
            detail=f"El tipo de empleado con ID {employee_data.id_type_employee} no existe"
        )

    # Validar duplicados
    if db.query(Employee).filter(Employee.first_name == employee_data.first_name, Employee.last_name == employee_data.last_name).first():
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El empleado ya existe"),
            headers={"X-Error": "El empleado ya existe"}
        )

    try:
        new_employee = Employee(
            id_type_employee=employee_data.id_type_employee,
            first_name=employee_data.first_name,
            last_name=employee_data.last_name,
            phone_number=employee_data.phone_number,
            state=employee_data.state,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        
        create_log(
            db,
            user_id=current_user.id_user,
            action="CREATE",
            entity="Employee",
            entity_id=new_employee.id_employee,
            description=f"El usuario {current_user.user} creó el empleado {new_employee.first_name} {new_employee.last_name}"
        )
        return success_response(EmployeeResponse.model_validate(new_employee).model_dump(mode="json"))
    except Exception as e:
        db.rollback()  
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al crear el empleado: {str(e)}").body.decode(),
            headers={"X-Error": f"Error al crear el empleado: {str(e)}"}
        )


@router.put('/{employee_id}', response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    employee = db.query(Employee).filter(Employee.id_employee == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El empleado no existe"),
            headers={"X-Error": "El empleado no existe"}
        )
    try:
        # Validar y actualizar tipo de empleado
        if employee_data.id_type_employee is not None:
            type_emp = db.query(TypeEmployee).filter(TypeEmployee.id_type_employee == employee_data.id_type_employee).first()
            if not type_emp:
                raise HTTPException(
                    status_code=404,
                    detail=f"El tipo de empleado con ID {employee_data.id_type_employee} no existe"
                )
            employee.id_type_employee = employee_data.id_type_employee

        # Actualizar campos opcionales
        for field in ["first_name", "last_name", "phone_number", "state"]:
            value = getattr(employee_data, field, None)
            if value is not None:
                setattr(employee, field, value)

        employee.updated_at = datetime.now()
        db.commit()
        db.refresh(employee)
        
        create_log(
            db,
            user_id=current_user.id_user,
            action="UPDATE",
            entity="Employee",
            entity_id=employee.id_employee,
            description=f"El usuario {current_user.user} actualizó el empleado {employee.first_name} {employee.last_name}"
        )
        
        return success_response(EmployeeResponse.model_validate(employee).model_dump(mode="json"))
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al actualizar el empleado: {str(e)}").body.decode(),
            headers={"X-Error": f"Error al actualizar el empleado: {str(e)}"}
        )


@router.delete('/{employee_id}', response_model=EmployeeResponse)
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    employee = db.query(Employee).filter(Employee.id_employee == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El empleado no existe"),
            headers={"X-Error": "El empleado no existe"}
        )

    try:
        # Alternar estado
        new_state = not employee.state
        employee.state = new_state
        employee.updated_at = datetime.now()
        db.commit()
        db.refresh(employee)
        
        action_text = "activó" if new_state else "desactivó"
        create_log(
            db,
            user_id=current_user.id_user,
            action="UPDATE",
            entity="Employee",
            entity_id=employee.id_employee,
            description=f"El usuario {current_user.user} {action_text} el empleado {employee.first_name} {employee.last_name}"
        )
        
        return success_response(f"Empleado {'activado' if new_state else 'desactivado'} exitosamente")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al desactivar el empleado: {str(e)}").body.decode(),
            headers={"X-Error": f"Error al desactivar el empleado: {str(e)}"}
        )