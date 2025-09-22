from fastapi import HTTPException, APIRouter
from app.models.tanks.tanks import Tank
from typing import List
from datetime import datetime
from app.schemas.tanks.tanks import TankBase, TankResponse
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin
from sqlalchemy import func

router = APIRouter(prefix='/tank', tags=['Tank'])

@router.get('', response_model=List[TankResponse])
async def get_tanks(
    page: int = 1, 
    limit: int = 5, 
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
    ):
    
    try: 
        offset = (page - 1) * limit
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
        tanks_with_coords = db.query(
            Tank,
            func.ST_Y(Tank.coordinates).label('latitude'),
            func.ST_X(Tank.coordinates).label('longitude')
        ).offset(offset).limit(limit).all()
        
        tank_list = []
        for tank, lat, lon in tanks_with_coords:
            tank_response = TankResponse(
                id_tank=tank.id_tank,
                name=tank.name,
                latitude=lat or 0.0,
                longitude=lon or 0.0,
                connections=tank.connections,
                photography=tank.photography,
                state=tank.state,
                created_at=tank.created_at,
                updated_at=tank.updated_at
            )
            tank_list.append(tank_response)

        return success_response([t.model_dump(mode="json") for t in tank_list])
    except Exception as e:
        return error_response(f"Error al obtener tanques: {str(e)}", 500)

@router.post('', response_model=TankResponse)
async def create_tank(
    tank_data: TankBase,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    if db.query(Tank).filter(Tank.name == tank_data.name).first():
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El tanque ya existe"),
            headers={"X-Error": "El tanque ya existe"}
        )
    try:
        new_tank = Tank(
            name = tank_data.name,
            coordinates = f"SRID=4326;POINT({tank_data.longitude} {tank_data.latitude})",
            connections = tank_data.connections,
            photography = tank_data.photography,
            state = tank_data.state,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        
        db.add(new_tank)
        db.commit()
        db.refresh(new_tank)
        tank_response = TankResponse(
            id_tank=new_tank.id_tank,
            name=new_tank.name,
            latitude=tank_data.latitude,
            longitude=tank_data.longitude,
            connections=new_tank.connections,
            photography=new_tank.photography,
            state=new_tank.state,
            created_at=new_tank.created_at,
            updated_at=new_tank.updated_at
            
        )
        return success_response(tank_response.model_dump(mode="json"))
    except Exception as e:
        db.rollback()
        return error_response(f"Error al crear el tanque: {str(e)}", 500)