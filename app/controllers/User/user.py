from fastapi import HTTPException, APIRouter,Depends
from app.models.user.user import Username
from typing import List
from datetime import datetime
from app.schemas.user.user import UserBase, UserResponse, UserUpdate
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.auth import get_password_hash
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin

router = APIRouter(prefix='/user', tags=['User'])

@router.get('', response_model = List[UserResponse])
async def get_user(
    page: int = 1,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    
    try: 
        offset = (page - 1) * limit
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
        usernames = db.query(Username).offset(offset).limit(limit).all()
        return success_response([
            UserResponse.model_validate(user).model_dump(mode="json")
            for user in usernames
            ])
    except Exception as e:
        return error_response(f"Error al obtener user: {str(e)}")

@router.post('',response_model = UserResponse)
async def create_user(
    user_data: UserBase, 
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
    ):
    if db.query(Username).filter(Username.user == user_data.user).first():
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El user ya existe"),
            headers={"X-Error": "El user ya existe"}
        )        
    
    hashed_password = get_password_hash(user_data.password_hash)
    
    try:
        new_user = Username(
            user=user_data.user,
            password_hash=hashed_password,
            email= user_data.email,
            employee_id=user_data.employee_id,
            rol_id=user_data.rol_id,
            status=user_data.status,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return success_response(UserResponse.model_validate(new_user).model_dump(mode="json"))
    except Exception as e:
        db.rollback()  
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al crear el user: {str(e)}").body.decode(),
            headers={"X-Error": f"Error al crear el user: {str(e)}"}
        )
        
@router.put('/{user_id}', response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,  # Usa UserUpdate en lugar de UserBase
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    # Buscar usuario
    user = db.query(Username).filter(Username.id_user == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El user no existe"),
            headers={"X-Error": "El user no existe"}
        )
    
    # Validar username único (solo si se proporciona y es diferente)
    if user_data.user and user.user != user_data.user:
        existing_user = db.query(Username).filter(Username.user == user_data.user).first()
        if existing_user:
            raise HTTPException(
                status_code=409,
                detail=existence_response_dict(True, "El user ya existe"),
                headers={"X-Error": "El user ya existe"}
            )
    
    # Validar email único (solo si se proporciona y es diferente)
    if user_data.email and user.email != user_data.email:
        existing_email = db.query(Username).filter(Username.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=409,
                detail=existence_response_dict(True, "El email ya está en uso"),
                headers={"X-Error": "El email ya está en uso"}
            )
    
    try:
        # Actualizar solo los campos proporcionados (no None)
        if user_data.user is not None:
            user.user = user_data.user
        
        # Solo hashear y actualizar si se envía una nueva contraseña
        if user_data.password is not None:
            user.password_hash = get_password_hash(user_data.password)
        
        if user_data.email is not None:
            user.email = user_data.email
        
        if user_data.employee_id is not None:
            user.employee_id = user_data.employee_id
        
        if user_data.rol_id is not None:
            user.rol_id = user_data.rol_id
        
        if user_data.status is not None:
            user.status = user_data.status
        
        user.updated_at = datetime.now()
        
        db.commit()
        db.refresh(user)
        return success_response(UserResponse.model_validate(user).model_dump(mode="json"))
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al actualizar el user: {str(e)}").body.decode(),
            headers={"X-Error": f"Error al actualizar el user: {str(e)}"}
        )
        
@router.delete('/{user_id}', response_model = UserResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    user = db.query(Username).filter(Username.id_user == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El user no existe"),
            headers={"X-Error": "El user no existe"}
        )

    try:
        user.status = 0
        user.updated_at = datetime.now()
        db.commit()
        db.refresh(user)
        return success_response("User desactivado exitosamente")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al desactivar el user: {str(e)}").body.decode(),
            headers={"X-Error": f"Error al desactivar el user: {str(e)}"}
        )