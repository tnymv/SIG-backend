from fastapi import HTTPException, APIRouter,Depends
from app.models.username.username import Username
from typing import List
from datetime import datetime
from app.schemas.username.username import UsernameBase, UsernameResponse
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.auth import get_password_hash

router = APIRouter(prefix='/username', tags=['Username'])

@router.get('', response_model = List[UsernameResponse])
async def get_usernames(
    page: int = 1,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    
    try: 
        offset = (page - 1) * limit
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
        usernames = db.query(Username).offset(offset).limit(limit).all()
        return success_response([
            UsernameResponse.model_validate(user).model_dump(mode="json")
            for user in usernames
            ])
    except Exception as e:
        return error_response(f"Error al obtener usernames: {str(e)}")

@router.post('',response_model = UsernameResponse)
async def create_username(username_data: UsernameBase, db: Session = Depends(get_db)):
    if db.query(Username).filter(Username.username == username_data.username).first():
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El username ya existe"),
            headers={"X-Error": "El username ya existe"}
        )        
    
    hashed_password = get_password_hash(username_data.password_hash)
    
    try:
        new_username = Username(
            username=username_data.username,
            password_hash=hashed_password,
            employee_id=username_data.employee_id,
            rol_id=username_data.rol_id,
            status=username_data.status,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(new_username)
        db.commit()
        db.refresh(new_username)
        return success_response(UsernameResponse.model_validate(new_username).model_dump(mode="json"))
    except Exception as e:
        db.rollback()  
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al crear el username: {str(e)}").body.decode(),
            headers={"X-Error": f"Error al crear el username: {str(e)}"}
        )