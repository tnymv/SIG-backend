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
from app.schemas.user.user import UserResponse
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

@router.get('/me', response_model=UserResponse)  #Este endpoint es para obtener la información del usuario actual
async def read_users_me(
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    
        create_log(
        db=db,
        user_id=current_user.id_user,
        action="READ",
        description=f"El usuario {current_user.user} consultó su información personal"
        )
        return current_user