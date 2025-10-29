from app.controllers.Tank.tank import get_all, get_by_id, create, update, toggle_state
from app.schemas.tanks.tanks import TankResponse, TankCreate, TankUpdate 
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response
from app.schemas.user.user import UserLogin
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List

router = APIRouter(prefix='/tank', tags=['Tank'])

@router.get('', response_model= List[TankResponse])
async def list_tanks(
    page: int = 1,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
): 
    try:
        tanks = get_all(db, page, limit)
        
        #Agregar el create log 

        return success_response([TankResponse.model_validate(emp).model_dump(mode="json")for emp in tanks])
    except Exception as e:
        return error_response(f"Error al obtener los tanques: {e}")

@router.get('/{tank_id}', response_model = TankResponse)
async def get_tank(
    tank_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        tank = get_by_id(db, tank_id)
        return success_response(TankResponse.model_validate(tank).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener el tipo de tanque: {e}")

@router.post('', response_model=TankResponse)
async def create_tank(
    data: TankCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        new_tank = create(db, data)
        return success_response(TankResponse.model_validate(new_tank).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear el tanque: {e}")

@router.put('/{tank_id}', response_model = TankResponse)
async def update_tank(
    tank_id: int,
    data: TankUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        tank_updated = update(db, tank_id, data)
        return success_response(TankResponse.model_validate(tank_updated).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar el tanque {e}")
    
@router.delete('/{tank_id}')
async def toggle_tank_state(
    tank_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
): 
    try:
        toggle_tank = toggle_state(db, tank_id)
        action = "activo" if toggle_tank.state else "inactivo"
        return success_response({
            "message": f"Se {action} el tanque '{toggle_tank.name}', correctamente."
        })
    except Exception as e:
        return error_response(f"Error al cambiar el estado del tanque: {e}")