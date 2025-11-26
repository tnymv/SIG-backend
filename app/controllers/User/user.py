from fastapi import HTTPException, APIRouter,Depends
from app.models.user.user import Username
from typing import List, Optional
from datetime import datetime
from app.schemas.user.user import UserBase, UserResponse, UserUpdate, UserCreate
from app.db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.auth import get_password_hash
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.logger import create_log
from app.schemas.user.user import UserLogin
        
def get_all(db: Session, page: int, limit: int, search: Optional[str] = None):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
    
    offset = (page - 1) * limit
    
    # Construir query base
    query = db.query(Username)
    
    # Aplicar búsqueda si se proporciona
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Username.user).like(search_term),
                func.lower(func.coalesce(Username.email, '')).like(search_term)
            )
        )
    
    # Contar total antes de paginar
    total = query.count()
    
    # Aplicar paginación
    user = query.order_by(Username.id_user.desc()).offset(offset).limit(limit).all()
    
    # Si no hay resultados pero hay búsqueda, no es un error, solo no hay coincidencias
    if not user and not search:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "No hay usuarios disponibles"),
            headers={"X-Error": "No hay usuarios disponibles"}
        )
    return user, total

def get_by_id(db: Session, id_user: int):
    user = db.query(Username).filter(Username.id_user == id_user).first()
    if not user:
        raise HTTPException(
            status_code = 404,
            detail=existence_response_dict(False, "El usuario no existe")
        )
    return user
        
def create(db: Session, data: UserCreate,current_user: UserLogin):
    existing = db.query(Username).filter(Username.user == data.user).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El usuario ya existe"),
            headers={"X-Error": "El usuario ya existe"}
        )
        
    hashed_password = get_password_hash(data.password_hash)
    
    new_user = Username(
                user=data.user,
                password_hash=hashed_password,
                email= data.email,
                employee_id=data.employee_id,
                rol_id=data.rol_id,
                active=data.active,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    create_log(
        db,
        user_id=current_user.id_user,
        action = "CREATE",
        entity = "User",
        entity_id=new_user.id_user,
        description=f"El usuario {current_user.user} creó el usuario {new_user.user}"
    ) 
    return new_user

def update(db: Session, id_user: int, data: UserUpdate,current_user: UserLogin):
    user_data = get_by_id(db, id_user)
    
    
    update_data = data.dict(exclude_unset=True)
    
    # Si se proporciona password, hashearlo y asignarlo a password_hash
    if 'password' in update_data and update_data['password']:
        hashed_password = get_password_hash(update_data['password'])
        user_data.password_hash = hashed_password
        del update_data['password']
    
    for field, value in update_data.items():
        setattr(user_data, field, value)

    user_data.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user_data)
    create_log(
        db,
        user_id=current_user.id_user,
        action = "UPDATE",
        entity = "User",
        entity_id=user_data.id_user,
        description=f"El usuario {current_user.user} actualizo el usuario {user_data.user}"
    ) 
    return user_data

def toggle_state(db: Session, id_user: int, current_user: UserLogin):
    user  = get_by_id(db, id_user)
    user.active = not user.active
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    status = ""
    if user.active is False:
        status = "inactivo"
    else: 
        status = "activo" 

    create_log(
        db,
        user_id=current_user.id_user,
        action = "TOGGLE",
        entity = "User",
        entity_id=user.id_user,
        description=f"El usuario {current_user.user}, {status} el usuario {user.user}"
    ) 
    return user
