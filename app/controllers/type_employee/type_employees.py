from app.schemas.type_employee.type_employees import TypeEmployeeUpdate, TypeEmployeeCreate
from app.models.type_employee.type_employees import TypeEmployee
from app.utils.response import existence_response_dict
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime 

def get_all(db: Session, page: int, limit: int):
    offset = (page - 1) * limit
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")   
    return db.query(TypeEmployee).offset(offset).limit(limit).all()

def get_by_id(db: Session, id_type_employee: int):
    type_employee = db.query(TypeEmployee).filter(TypeEmployee.id_type_employee == id_type_employee).first()
    if not type_employee:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El tipo de empleado no existe")
        )
    return type_employee

def create(db: Session, data: TypeEmployeeCreate):
    existing = db.query(TypeEmployee).filter(TypeEmployee.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El tipo de empleado ya existe"),
            headers={"X-Error": "El tipo de empleado ya existe"}
        )

    new_type_employee = TypeEmployee(
        name=data.name,
        description=data.description,
        state=data.state,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_type_employee)
    db.commit()
    db.refresh(new_type_employee)
    return new_type_employee

def update(db: Session, id_type_employee: int, data: TypeEmployeeUpdate):
    type_employee = get_by_id(db, id_type_employee)
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(type_employee, field, value)
        
    type_employee.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(type_employee)
    return type_employee

def toggle_state(db: Session, id_type_employee: int):
    type_employee = get_by_id(db, id_type_employee)
    type_employee.state = not type_employee.state
    type_employee.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(type_employee)
    return type_employee