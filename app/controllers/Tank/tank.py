from fastapi import HTTPException, APIRouter
from app.models.tanks.tanks import Tank
from typing import List
from datetime import datetime
from app.schemas.tanks.tanks import TankBase, TankResponse, TankResponseCreate, TankUpdate
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin
from sqlalchemy import func

router = APIRouter(prefix='/tank', tags=['Tank'])


@router.post('', response_model=TankResponseCreate)  # ← Agregar response_model
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
            name=tank_data.name,
            coordinates=f"SRID=4326;POINT({tank_data.longitude} {tank_data.latitude})",
            connections=tank_data.connections,
            photography=tank_data.photography if tank_data.photography else [],
            state=tank_data.state,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(new_tank)
        db.commit()
        db.refresh(new_tank)
        
        # Convertir arrays de PostgreSQL a listas de Python
        photography_list = list(new_tank.photography) if new_tank.photography else []
        
        tank_response = TankResponseCreate(
            id_tank=new_tank.id_tank,
            name=new_tank.name,
            latitude=tank_data.latitude,
            longitude=tank_data.longitude,
            connections=tank_data.connections,
            state=new_tank.state,
            created_at=new_tank.created_at,
            updated_at=new_tank.updated_at
        )
        
        return success_response(tank_response.model_dump(mode="json"))
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear el tanque: {str(e)}")
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el tanque: {str(e)}",
            headers={"X-Error": f"Error al crear el tanque: {str(e)}"}
        )
        
@router.put('/{tank_id}', response_model=TankResponse)
async def update_tank(
    tank_id: int,
    tank_data: TankUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    #Buscar tanque
    tank = db.query(Tank).filter(Tank.id_tank == tank_id).first()
    if not tank:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El tanque no existe"),
            headers={"X-Error": "El tanque no existe"}
        )

    #Validar si el nuevo nombre ya existe en otro tanque
    if tank_data.name and tank_data.name != tank.name:
        existin_tank = db.query(Tank).filter(Tank.name == tank_data.name).first()
        if existin_tank:
            raise HTTPException(
                status_code=409,
                detail=existence_response_dict(True, "El nombre del tanque ya existe"),
                headers={"X-Error": "El nombre del tanque ya existe"}
            )
    
    try:
        # Actualizar solo los campos proporcionados (no None)
        if tank_data.name is not None:
            tank.name = tank_data.name
            
        if tank_data.latitude is not None and tank_data.longitude is not None:
            tank.coordinates = f"SRID=4326;POINT({tank_data.longitude} {tank_data.latitude})"
        elif tank_data.latitude is not None or tank_data.longitude is not None:
            raise HTTPException(
                status_code=400,
                detail="Ambos campos latitude y longitude deben ser proporcionados juntos.",
                headers={"X-Error": "Campos de coordenadas incompletos"}
            )
        if tank_data.connections is not None:
            tank.connections = tank_data.connections
            
        if tank_data.photography is not None:
            tank.photography = tank_data.photography
        if tank_data.state is not None:
            tank.state = tank_data.state
        tank.updated_at = datetime.now()
        
        db.commit()
        db.refresh(tank)
        photography_list = list(tank.photography) if tank.photography else []
        longitude, latitude = map(float, tank.coordinates.split('(')[1].strip(')').split())
        
        tank_response = TankResponse(
            id_tank=tank.id_tank,
            name=tank.name,
            latitude=latitude,
            longitude=longitude,
            connections=tank.connections,
            state=tank.state,
            created_at=tank.created_at,
            updated_at=tank.updated_at
        )

        return success_response(tank_response.model_dump(mode="json"))

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar el tanque: {str(e)}")