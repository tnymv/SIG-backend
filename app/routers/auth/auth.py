from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.utils.logger import create_log

from app.utils.auth import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.schemas.auth.auth import Token
from app.schemas.user.user import UserResponse, UserResponseWithPermissions
from app.db.database import get_db
from app.controllers.auth.auth_controller import authenticate_user, get_current_active_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post('/token', response_model=Token)  
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    create_log(
        db,
        user_id=user.id_user,
        action="LOGIN",
        description=f"El usuario {user.user} inició sesión"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get('/me', response_model=UserResponseWithPermissions)  #Este endpoint es para obtener la información del usuario actual
async def read_users_me(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Obtener información del rol
    rol_info = None
    if current_user.rol:
        rol_info = {
            "id_rol": current_user.rol.id_rol,
            "name": current_user.rol.name,
            "description": current_user.rol.description,
            "status": current_user.rol.status
        }
    
    permissions = []
    if current_user.rol and current_user.rol.permissions:
        active_permissions = [perm for perm in current_user.rol.permissions if perm.status]
        permissions = [
            {
                "id_permissions": perm.id_permissions,
                "name": perm.name,
                "description": perm.description,
                "status": perm.status
            }
            for perm in active_permissions
        ]
    
    user_response = UserResponseWithPermissions(
        id_user=current_user.id_user,
        user=current_user.user,
        password_hash=current_user.password_hash,
        email=current_user.email,
        employee_id=current_user.employee_id,
        rol_id=current_user.rol_id,
        status=current_user.status,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        rol=rol_info,
        permissions=permissions
    )
    
    create_log(
        db=db,
        user_id=current_user.id_user,
        action="READ",
        description=f"El usuario {current_user.user} consultó su información personal"
    )
    return user_response