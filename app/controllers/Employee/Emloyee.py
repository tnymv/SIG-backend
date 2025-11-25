from app.schemas.employee.employee import  EmployeeUpdate, EmployeeCreate
from app.models.type_employee.type_employees import TypeEmployee
from app.utils.response import  existence_response_dict
from app.models.employee.employee import Employee
from app.schemas.user.user import UserLogin
from app.utils.logger import create_log
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException
from datetime import datetime
from typing import Optional

def get_all(db: Session, page: int, limit: int, search: Optional[str] = None):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
    
    offset = (page - 1) * limit
    
    # Construir query base
    query = db.query(Employee)
    
    # Aplicar búsqueda si se proporciona
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Employee.first_name).like(search_term),
                func.lower(Employee.last_name).like(search_term),
                func.lower(func.coalesce(Employee.phone_number, '')).like(search_term)
            )
        )
    
    # Contar total antes de paginar
    total = query.count()
    
    # Aplicar paginación
    data_employee = query.order_by(Employee.id_employee.desc()).offset(offset).limit(limit).all()
    
    # Si no hay resultados pero hay búsqueda, no es un error, solo no hay coincidencias
    if not data_employee and not search:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "No hay empleados disponibles"),
            headers={"X-Error": "No hay empleados disponibles"}
        )
    return data_employee, total

def get_by_id(db: Session, Employee_id: int):
    employee = db.query(Employee).filter(Employee.id_employee == Employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El empleado no existe")
        )
    return employee

def create(db: Session, employee_data: EmployeeCreate, current_user: UserLogin):
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
    
    new_employee = Employee(
            id_type_employee=employee_data.id_type_employee,
            first_name=employee_data.first_name,
            last_name=employee_data.last_name,
            phone_number=employee_data.phone_number,
            active=employee_data.active,
            created_at=datetime.now(),
            updated_at=datetime.now()
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    create_log(
        db,
        user_id=current_user.id_user,
        action = "CREATE",
        entity = "Employee",
        entity_id=new_employee.id_employee,
        description=f"El usuario {current_user.user} creó el usuario {new_employee.first_name}"
    ) 
    return new_employee

def update(db: Session, employee_id: int, data: EmployeeUpdate, current_user: UserLogin):
    employee = get_by_id(db, employee_id)
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(employee,field,value)
        
    employee.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(employee)
    create_log(
        db,
        user_id=current_user.id_user,
        action = "UPDATE",
        entity = "Employee",
        entity_id=employee.id_employee,
        description=f"El usuario {current_user.user} actualizo el usuario {employee.first_name}"
    ) 
    return employee

def toggle_state(db: Session, employee_id: int, current_user: UserLogin):
    employee = get_by_id(db, employee_id)
    employee.active = not employee.active
    employee.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(employee)
    
    status = ""
    if employee.active is False:
        status = "inactivo"
    else: 
        status = "activo" 
        
    create_log(
        db,
        user_id=current_user.id_user,
        action = "TOGGLE",
        entity = "Employee",
        entity_id=employee.id_employee,
        description=f"El usuario {current_user.user}, {status} el usuario {employee.first_name}"
    ) 
    return employee 