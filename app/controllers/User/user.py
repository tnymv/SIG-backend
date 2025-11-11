from fastapi import HTTPException, APIRouter,Depends
from app.models.user.user import Username
from typing import List
from datetime import datetime
from app.schemas.user.user import UserBase, UserResponse, UserUpdate, UserCreate
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.auth import get_password_hash
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.logger import create_log
from app.schemas.user.user import UserLogin
        
def get_all(db: Session, page: int, limit: int):
    offset = (page - 1) * limit
    
    query = db.query(Username)
    total = query.count()
    
    user = db.query(Username).offset(offset).limit(limit).all()
    
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
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
                status=data.status,
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
    
    for field, value in data.dict(exclude_unset = True).items():
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
    user.status = not user.status
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    status = ""
    if user.status is False:
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
