from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from app.utils.auth import (
    verify_password,
    verify_token,
)
from app.schemas.user.user import UserResponse
from app.models.user.user import Username as username_model
from app.db.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

router = APIRouter(prefix='/auth', tags=['Authentication'])

def get_user(db: Session, email: str): #Esta función es para obtener al usuario
    return db.query(username_model).filter(username_model.email == email).first()

def get_user_with_permissions(db: Session, email: str): #Obtener usuario con rol y permisos cargados
    return db.query(username_model).options(
        joinedload(username_model.rol).joinedload(username_model.rol.property.mapper.class_.permissions)
    ).filter(username_model.email == email).first()

def authenticate_user(db: Session, username: str, password: str): #Esto sirve para autenticar al usuario
    # Buscar por email o por nombre de usuario
    user = db.query(username_model).filter(
        (username_model.email == username) | (username_model.user == username)
    ).first()
    if not user: 
        return False
    if not verify_password(password, user.password_hash):
        return False
    if not user.active: #Ver si se agrega, un mensaje que diga que el usuario no está activo
        return False
    return user

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)): #Esto nos ayuda para obtener el usuario actual del token
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "No se pudieron validar las credenciales",
        headers = {"WWW-Authenticate": "Bearer"},
    )
    email = verify_token(token, credentials_exception)
    user = get_user(db, email=email)
    if user is None: 
        raise credentials_exception
    
    from app.models.rol.rol import Rol
    user_with_rol = db.query(username_model).options(
        joinedload(username_model.rol).joinedload(Rol.permissions)
    ).filter(username_model.id_user == user.id_user).first()
    
    return user_with_rol if user_with_rol else user

def get_current_active_user(current_user: UserResponse = Depends(get_current_user)): #Esto nos sirve para verificar si el usuario está activo
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user