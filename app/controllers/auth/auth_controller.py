from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.schemas.auth.auth import Token, TokenData
from app.schemas.user.user import UserLogin
from app.models.user.user import Username as username_model
from app.db.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

router = APIRouter(prefix='/auth', tags=['Authentication'])

def get_user(db: Session, username: str): #Esta función es para obtener al usuario
    return db.query(username_model).filter(username_model.username == username).first()

def authenticate_user(db: Session, username: str, password: str): #Esto sirve para autenticar al usuario
    user = get_user(db, username)
    if not user: 
        return False
    if not verify_password(password, user.password_hash):  
        return False
    return user

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)): #Esto nos ayuda para obtener el usuario actual del token
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "No se pudieron validar las credenciales",
        headers = {"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token, credentials_exception)
    user = get_user(db, username=username)
    if user is None: 
        raise credentials_exception
    return user

def get_current_active_user(current_user: UserLogin = Depends(get_current_user)): #Esto nos sirve para verificar si el usuario está activo
    if not current_user.status:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

@router.post('/token', response_model=Token)   #Este es el endpoint para el login y obtener el token
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get('/me', response_model=UserLogin)  #Este endpoint es para obtener la información del usuario actual
async def read_users_me(current_user: UserLogin = Depends(get_current_active_user)):
    return current_user