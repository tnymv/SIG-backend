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

# router = APIRouter(prefix='/premissions', tags=['Permissions'])

# @router.get('', response_model=List[PermissionsResponse]) 
# async def get_permissions(
#     page: int = 1, limit: int = 5,
#     db: Session = Depends(get_db),
#     current_user: UserLogin = Depends(get_current_active_user)
#     ):

#     try:
#         offset = (page - 1) * limit
#         if page < 1 or limit < 1:
#          raise HTTPException(status_code=400, detail="La pagina y el limite deber ser mayores que 0")
#         permissions = db.query(Permissions).offset(offset).limit(limit).all()
#         return success_response([PermissionsResponse.model_validate(emp).model_dump(mode="json") for emp in permissions])
#     except Exception as e:
#         return error_response(f"Error al otener permisos: {str(e)}")

# @router.post('', response_model=PermissionsResponse)
# async def create_permissions(
#     permission_data: PermissionsBase,
#     db: Session = Depends(get_db),
#     current_user: UserLogin = Depends(get_current_active_user)
#     ):
#     if db.query(Permissions).filter(Permissions.name == permission_data.description).first():
#         raise HTTPException(
#             status_code=409,
#             detail=existence_response_dict(True, "El permiso ya existe"),
#             headers={"X-Error": "El permiso ya existe"}
#         )

#     try: 
#         new_permission = Permissions(
#             name=permission_data.name,
#             description=permission_data.description,
#             created_at=datetime.now(),
#             updated_at=datetime.now()
#         )
#         db.add(new_permission)
#         db.commit()
#         db.refresh(new_permission)

#         return success_response(PermissionsResponse.model_validate(new_permission).model_dump(mode="json"))
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=error_response(f"Error al crear el permiso: {str(e)}").body.decode(),
#             headers={"X-Error": f"Error al crear el permiso: {str(e)}"}
#         )
    
# @router.put('/{permissions_id}', response_model=PermissionsResponse)
# async def update_permissions(
#     permissions_id: int,
#     permissions_data: PermissionsUpdate,
#     db: Session = Depends(get_db),
#     current_user: UserLogin = Depends(get_current_active_user)
# ):
#     permissions = db.query(Permissions).filter(Permissions.id_permissions == permissions_id).first()
#     if not permissions:
#         raise HTTPException(
#             status_code=404,
#             detail=existence_response_dict(False, "El permiso no existe"),
#             headers={"X-Error": "El permiso no existe"}
#         )
    
#     try:
#         if permissions_data.name is not None: 
#             permissions.name = permissions_data.name
        
#         if permissions_data.description is not None:
#             permissions.description = permissions_data.description

#         if permissions_data.status is not None:
#             permissions.status = permissions_data.status
        
#         permissions.updated_at = datetime.now()

#         db.commit()
#         db.refresh(permissions)

#         create_log(
#             db,
#             user_id = current_user.id_user,
#             action= "UPDATE",
#             entity= "Permissions",
#             entity_id= permissions.id_permissions,
#             description= f"El usuario {current_user.user} actualizó el archivo {permissions.name} {permissions.description}"
#         )

#         return success_response(PermissionsResponse.model_validate(permissions).model_dump(mode="json"))
    
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=error_response(f"Error al actualizar el permiso: {str(e)}").body.decode(),
#             headers={"X-Error": f"Error al actualizar el permiso: {str(e)}"}
#         )
    
# @router.delete('/{permissions_id}', response_model=PermissionsResponse)
# async def delete_permissions(
#     permissions_id: int,
#     db: Session = Depends(get_db),
#     current_user: UserLogin = Depends(get_current_active_user)
# ):
#     permissions = db.query(Permissions).filter(Permissions.id_permissions== permissions_id).first()
#     if not permissions:
#         raise HTTPException(
#             status_code=404,
#             detail=existence_response_dict(False, "El permiso no existe"),
#             headers={"X-Error": "El permiso no existe"}
#         )

#     try: 
#         new_status = not permissions.status
#         permissions.status = new_status
#         permissions.updated_at = datetime.now()
#         db.commit()
#         db.refresh(permissions)

#         action_text = "activó" if new_status else "desactivó"
#         create_log(
#             db,
#             user_id = current_user.id_user,
#             action= "UPDATE",
#             entity= "Permisos",
#             entity_id= permissions.id_permissions,
#             description= f"El usuario {current_user.user} {action_text} el empleado {permissions.name} {permissions.description}"
#         )

#         return success_response(f"Archivo {'activado' if new_status else 'desactivado'} exitosamente")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=error_response(f"Error al desactivar el permiso: {str(e)}").body.decode(),
#             headers={"X-Error": f"Error al desactivar el permiso: {str(e)}"}
#         )
        
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

def create(db: Session, data: PermissionsCreate):
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
    return new_permission

def update(db: Session, permission_id: int, data: PermissionsUpdate):
    permission = get_by_id(db, permission_id)
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(permission, field, value)
    
    permission.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(permission)
    return permission

def toggle_state(db: Session, permission_id: int):
    permission = get_by_id(db, permission_id)
    permission.status = not permission.status 
    permission.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(permission)
    return permission
    