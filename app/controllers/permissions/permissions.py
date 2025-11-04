from fastapi import HTTPException, APIRouter
from app.models.permissions.permissions import Permissions
from typing import List
from datetime import datetime
from app.schemas.permissions.permissions import PermissionsBase, PermissionsResponse, PermissionsCreate, PermissionsUpdate
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.logger import create_log
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin

def get_all(db: Session, page: int, limit: int):
    offset = (page - 1) * limit
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")   
    return db.query(Permissions).offset(offset).limit(limit).all()

def get_by_id(db: Session, permissions_id: int):
    permissions = db.query(Permissions).filter(Permissions.id_permissions == permissions_id).first()
    if not permissions:
        raise HTTPException(
            status_code=404,
            detail = existence_response_dict(False, "Los permiso no existe") 
        )
    return permissions

def create(db: Session, data: PermissionsCreate,current_user: UserLogin):
    existing = db.query(Permissions).filter(Permissions.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El permiso ya existe"),
            headers={"X-Error": "El permiso ya existe"}
        )
    new_permission = Permissions(
            name=data.name,
            description=data.description,
            status=data.status,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    create_log(
        db,
        user_id=current_user.id_user,
        action = "CREATE",
        entity = "Permission",
        entity_id=new_permission.id_permissions,
        description=f"El usuario {current_user.user} creó el permiso {new_permission.name}"
    ) 
    return new_permission

def update(db: Session, permission_id: int, data: PermissionsUpdate,current_user: UserLogin):
    permission = get_by_id(db, permission_id)
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(permission, field, value)
    
    permission.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(permission)
    create_log(
        db,
        user_id=current_user.id_user,
        action = "UPDATE",
        entity = "Permission",
        entity_id=permission.id_permissions,
        description=f"El usuario {current_user.user} actualizo el permiso {permission.name}"
    ) 
    return permission

def toggle_state(db: Session, permission_id: int,current_user: UserLogin):
    permission = get_by_id(db, permission_id)
    permission.status = not permission.status 
    permission.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(permission)
    
    state = ""
    if permission.status is False:
        state = "inactivo"
    else: 
        state = "activo" 
    create_log(
        db,
        user_id=current_user.id_user,
        action = "TOGGLE",
        entity = "Permission",
        entity_id=permission.id_permissions,
        description=f"El usuario {current_user.user}, {state} el permiso {permission.name}"
    ) 
    return permission
    