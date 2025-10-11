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
from app.utils.logger import create_log
from sqlalchemy import func

router = APIRouter(prefix='/tank', tags=['Tank'])

@router.get('', response_model=List[TankResponse])  
async def get_all_tanks(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 5,
    current_user: UserLogin = Depends(get_current_active_user)
):

    try:
        if page < 1 or limit < 1:
            raise HTTPException(
                status_code=400, 
                detail="La página y el límite deben ser mayores que 0"
            )
        offset = (page - 1) * limit
        tanks = db.query(
            Tank,
            func.ST_X(Tank.coordinates).label('longitude'),
            func.ST_Y(Tank.coordinates).label('latitude')
        ).offset(offset).limit(limit).all()
        
        if not tanks:
            return success_response([])

        tanks_response = []
        for tank, longitude, latitude in tanks:
            photography_list = list(tank.photography) if tank.photography else []
            
            tank_response = TankResponse(
                id_tank=tank.id_tank,
                name=tank.name,
                latitude=latitude,
                longitude=longitude,
                connections=tank.connections,
                photography=photography_list,
                state=tank.state,
                created_at=tank.created_at,
                updated_at=tank.updated_at
            )
            
            tanks_response.append(tank_response.model_dump(mode="json"))

        create_log(
            db,
            user_id = current_user.id_user,
            action = "READ",
            entity = "Tank",
            description= f"El usuario {current_user.user} accedió a la lista de tanques"
        )
        return success_response(tanks_response)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los tanques: {str(e)}",
            headers={"X-Error": f"Error al obtener los tanques: {str(e)}"}
        )

@router.get('/{tank_id}', response_model=TankResponse)
async def get_tank_by_id(
    tank_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):

    try:
        result = db.query(
            Tank,
            func.ST_X(Tank.coordinates).label('longitude'),
            func.ST_Y(Tank.coordinates).label('latitude')
        ).filter(Tank.id_tank == tank_id).first()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=existence_response_dict(False, "El tanque no existe"),
                headers={"X-Error": "El tanque no existe"}
            )
        
        tank, longitude, latitude = result
        
        photography_list = list(tank.photography) if tank.photography else []
        
        tank_response = TankResponse(
            id_tank=tank.id_tank,
            name=tank.name,
            latitude=latitude,
            longitude=longitude,
            connections=tank.connections,
            photography=photography_list,
            state=tank.state,
            created_at=tank.created_at,
            updated_at=tank.updated_at
        )
        
        create_log(
            db,
            user_id = current_user.id_user,
            action = "READ",
            entity = "Tank",
            description= f"El usuario {current_user.user} accedió a la lista de tanques"
        )
        return success_response(tank_response.model_dump(mode="json"))
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el tanque: {str(e)}",
            headers={"X-Error": f"Error al obtener el tanque: {str(e)}"}
        )

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
        create_log(
            db,
            user_id = current_user.id_user,
            action = "CREATE",
            entity = "Tank",
            description= f"El usuario {current_user.user} creó un nuevo tanque"
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
        create_log(
            db,
            user_id = current_user.id_user,
            action = "PUT",
            entity = "Tank",
            description= f"El usuario {current_user.user} actualizó el tanque {tank.id_tank}"
        )
        return success_response(tank_response.model_dump(mode="json"))

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar el tanque: {str(e)}")
    
@router.delete('/{tank_id}', response_model = TankResponse)
async def delete_tank(
    tank_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    tank = db.query(Tank).filter(Tank.id_tank == tank_id).first()
    if not tank:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El tanque no existe"),
            headers={"X-Error": "El tanque no existe"}
        )
        
    try:
        tank.state = False
        tank.updated_at = datetime.now()
        db.commit()
        db.refresh(tank)
        create_log(
            db,
            user_id = current_user.id_user,
            action = "DELETE",
            entity = "Tank",
            description= f"El usuario {current_user.user} eliminó el tanque {tank.id_tank}z"
        )   
        return success_response("Tanque eliminado exitosamente")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al eliminar el tanque: {str(e)}").body.decode(),
            headers={"X-Error": f"Error al eliminar el tanque: {str(e)}"}
        )