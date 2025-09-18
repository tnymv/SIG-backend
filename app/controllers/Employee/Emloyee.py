from fastapi import HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm #Para poder usar OAuth2
from app.models.employee.employee import Employee
from typing import List
from datetime import datetime
from app.schemas.employee.employee import EmployeeBase, EmployeeResponse, EmployeeCreate
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict

router = APIRouter(prefix='/employee', tags=['Employee'])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get('', response_model=List[EmployeeResponse])
async def get_employees(page: int = 1, limit: int = 5, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        offset = (page - 1) * limit
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
        employees = db.query(Employee).offset(offset).limit(limit).all()
        return success_response([EmployeeResponse.model_validate(emp).model_dump(mode="json") for emp in employees])
    except Exception as e:
        return error_response(f"Error al obtener empleados: {str(e)}")

@router.post('', response_model=EmployeeResponse)
async def create_employee(employee_data: EmployeeBase, db: Session = Depends(get_db)):
    if db.query(Employee).filter(Employee.first_name == employee_data.first_name).first():
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El empleado ya existe"),
            headers={"X-Error": "El empleado ya existe"}
        )

    try:
        new_employee = Employee(
            first_name=employee_data.first_name,
            last_name=employee_data.last_name,
            email=employee_data.email,
            phone_number=employee_data.phone_number,
            status=employee_data.status,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        return success_response(EmployeeResponse.model_validate(new_employee).model_dump(mode="json"))
    except Exception as e:
        db.rollback()  
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al crear el empleado: {str(e)}").body.decode(),
            headers={"X-Error": f"Error al crear el empleado: {str(e)}"}
        )