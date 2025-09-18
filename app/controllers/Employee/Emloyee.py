from fastapi import HTTPException, APIRouter
from app.models.employee.employee import Employee
from typing import List
from datetime import datetime
from app.schemas.employee.employee import EmployeeBase, EmployeeResponse, EmployeeCreate
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter(prefix='/employee', tags=['Employee']) 

@router.get('', response_model=List[EmployeeResponse])
async def get_employees(page: int = 1, limit: int = 5, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    employees = db.query(Employee).offset(offset).limit(limit).all()
    return employees

@router.post('', response_model=EmployeeResponse)
async def create_employee(employee_data: EmployeeBase, db: Session = Depends(get_db)):
    if db.query(Employee).filter(Employee.first_name == employee_data.first_name).first():
        raise HTTPException(
            status_code=409,
            detail="El empleado ya existe",
            headers={"X-Error": "El empleado ya existe"}
        )

    try:
        new_employee = Employee(
            first_name=employee_data.name,
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
        return new_employee

        return EmployeeResponse.model_validate(new_employee)
    except Exception as e:
        db.rollback()  
        raise HTTPException(
            status_code=400,
            detail=str(e),
            headers={"X-Error": str(e)}
        )