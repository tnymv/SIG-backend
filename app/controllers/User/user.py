from fastapi import HTTPException, APIRouter,Depends
from app.models.user.user import User
from typing import List
from datetime import datetime
from app.schemas.user.user import UserBase, UserResponse
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.auth import get_password_hash

router = APIRouter(prefix='/user', tags=['User'])

@router.get('', response_model = List[UserResponse])
async def get_user(
    page: int = 1,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    
    try: 
        offset = (page - 1) * limit
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
        usernames = db.query(User).offset(offset).limit(limit).all()
        return success_response([
            UserResponse.model_validate(user).model_dump(mode="json")
            for user in usernames
            ])
    except Exception as e:
        return error_response(f"Error al obtener usernames: {str(e)}")

@router.post('',response_model = UserResponse)
async def create_user(user_data: UserBase, db: Session = Depends(get_db)):
    if db.query(User).filter(User.user == user_data.user).first():
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El user ya existe"),
            headers={"X-Error": "El user ya existe"}
        )        
    
    hashed_password = get_password_hash(user_data.password_hash)
    
    try:
        new_user = User(
            user=user_data.user,
            password_hash=hashed_password,
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