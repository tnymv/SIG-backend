from app.schemas.type_employee.type_employees import TypeEmployeeUpdate, TypeEmployeeCreate
from app.models.type_employee.type_employees import TypeEmployee
from app.utils.response import existence_response_dict
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime 
from typing import Optional
from app.schemas.user.user import UserLogin
from app.utils.logger import create_log

def get_all(db: Session, page: int, limit: int, search: Optional[str] = None):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
    
    offset = (page - 1) * limit
    
    # Construir query base
    query = db.query(TypeEmployee)
    
    # Aplicar búsqueda si se proporciona
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(TypeEmployee.name).like(search_term),
                func.lower(func.coalesce(TypeEmployee.description, '')).like(search_term)
            )
        )
    
    # Contar total antes de paginar
    total = query.count()
    
    # Aplicar paginación
    type_employee_q = query.offset(offset).limit(limit).all()
    
    # Si no hay resultados pero hay búsqueda, no es un error, solo no hay coincidencias
    if not type_employee_q and not search:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "No hay tipos de empleado disponibles"),
            headers={"X-Error": "No hay tipos de empleado disponibles"}
        )
    return type_employee_q, total

def get_by_id(db: Session, id_type_employee: int):
    type_employee = db.query(TypeEmployee).filter(TypeEmployee.id_type_employee == id_type_employee).first()
    if not type_employee:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El tipo de empleado no existe")
        )
    return type_employee

def create(db: Session, data: TypeEmployeeCreate,current_user: UserLogin):
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
    create_log(
        db,
        user_id=current_user.id_user,
        action = "CREATE",
        entity = "Type_employee",
        entity_id=new_type_employee.id_type_employee,
        description=f"El usuario {current_user.user} creó el permiso {new_type_employee.name}"
    ) 
    return new_type_employee

def update(db: Session, id_type_employee: int, data: TypeEmployeeUpdate,current_user: UserLogin):
    type_employee = get_by_id(db, id_type_employee)
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(type_employee, field, value)
        
    type_employee.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(type_employee)
    create_log(
        db,
        user_id=current_user.id_user,
        action = "UPDATE",
        entity = "Permission",
        entity_id=type_employee.id_type_employee,
        description=f"El usuario {current_user.user} actualizo el permiso {type_employee.name}"
    ) 
    return type_employee

def toggle_state(db: Session, id_type_employee: int,current_user: UserLogin):
    type_employee = get_by_id(db, id_type_employee)
    type_employee.state = not type_employee.state
    type_employee.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(type_employee)
    status = ""
    if type_employee.state is False:
        status = "inactivo"
    else: 
        status = "activo" 
    create_log(
        db,
        user_id=current_user.id_user,
        action = "TOGGLE",
        entity = "Permission",
        entity_id=type_employee.id_type_employee,
        description=f"El usuario {current_user.user}, {status} el permiso {type_employee.name}"
    ) 
    return type_employee