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
        
        import json
        
        tank_list = []
        for tank, lat, lon in tanks_with_coords:
            # Deserializar fotos desde JSON
            photos = []
            if tank.photography:
                try:
                    # Intentar deserializar como JSON (nuevo formato)
                    photos = json.loads(tank.photography)
                    if not isinstance(photos, list):
                        photos = [tank.photography]  # Fallback para formato antiguo
                except (json.JSONDecodeError, TypeError):
                    # Formato antiguo: string simple
                    photos = [tank.photography] if tank.photography else []
            
            tank_response = TankResponse(
                id_tank=tank.id_tank,
                name=tank.name,
                latitude=lat or 0.0,
                longitude=lon or 0.0,
                connections=tank.connections,
                photos=photos,
                photography=photos[0] if photos else None,  # Compatibilidad
                state=tank.state,
                created_at=tank.created_at,
                updated_at=tank.updated_at
            )
            tank_list.append(tank_response)

        return success_response([t.model_dump(mode="json") for t in tank_list])
    except Exception as e:
        return error_response(f"Error al obtener tanques: {str(e)}", 500)
    
@router.get('/{tank_id}', response_model=TankResponse)
async def get_tank_by_id(
    tank_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        tank_with_coords = db.query(
            Tank,
            func.ST_Y(Tank.coordinates).label('latitude'),
            func.ST_X(Tank.coordinates).label('longitude')
        ).filter(Tank.id_tank == tank_id).first()
        
        if not tank_with_coords:
            raise HTTPException(
                status_code=404,
                detail=existence_response_dict(False, "El tanque no existe"),
                headers={"X-Error": "El tanque no existe"}
            )
        
        tank, lat, lon = tank_with_coords
        
        import json
        
        photos = []
        if tank.photography:
            try:
                photos = json.loads(tank.photography)
                if not isinstance(photos, list):
                    photos = [tank.photography]
            except (json.JSONDecodeError, TypeError):
                photos = [tank.photography] if tank.photography else []
        
        tank_response = TankResponse(
            id_tank=tank.id_tank,
            name=tank.name,
            latitude=lat or 0.0,
            longitude=lon or 0.0,
            connections=tank.connections,
            photos=photos,
            photography=photos[0] if photos else None,  # Compatibilidad
            state=tank.state,
            created_at=tank.created_at,
            updated_at=tank.updated_at
        )
        
        return success_response(tank_response.model_dump(mode="json"))
    except HTTPException as he:
        raise he
    except Exception as e:
        return error_response(f"Error al obtener el tanque: {str(e)}", 500)
        

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
        import json
        
        # Manejar fotos: usar el array photos si está disponible, sino usar photography
        photos_to_store = tank_data.photos if tank_data.photos else []
        if tank_data.photography and tank_data.photography not in photos_to_store:
            photos_to_store.append(tank_data.photography)
        
        # Guardar fotos como JSON string
        photography_json = json.dumps(photos_to_store) if photos_to_store else None
        
        new_tank = Tank(
            name = tank_data.name,
            coordinates = f"SRID=4326;POINT({tank_data.longitude} {tank_data.latitude})",
            connections = tank_data.connections,
            photography = photography_json,
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
            photos=photos_to_store,
            photography=photos_to_store[0] if photos_to_store else None,
            state=new_tank.state,
            created_at=new_tank.created_at,
            updated_at=new_tank.updated_at
        )
        return success_response(tank_response.model_dump(mode="json"))
    except Exception as e:
        db.rollback()
        return error_response(f"Error al crear el tanque: {str(e)}", 500)
    
@router.put('/{tank_id}', response_model=TankResponse)
async def update_tank(
    tank_id: int,
    tank_data: TankBase,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    existing_tank = db.query(Tank).filter(Tank.id_tank == tank_id).first()
    if not existing_tank:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El tanque no existe"),
            headers={"X-Error": "El tanque no existe"}
        )
    
    if db.query(Tank).filter(Tank.name == tank_data.name, Tank.id_tank != tank_id).first():
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El nombre del tanque ya está en uso"),
            headers={"X-Error": "El nombre del tanque ya está en uso"}
        )
    
    try:
        import json
        
        # Manejar fotos: usar el array photos si está disponible, sino usar photography
        photos_to_store = tank_data.photos if tank_data.photos else []
        if tank_data.photography and tank_data.photography not in photos_to_store:
            photos_to_store.append(tank_data.photography)
        
        # Guardar fotos como JSON string
        photography_json = json.dumps(photos_to_store) if photos_to_store else None
        
        existing_tank.name = tank_data.name
        existing_tank.coordinates = f"SRID=4326;POINT({tank_data.longitude} {tank_data.latitude})"
        existing_tank.connections = tank_data.connections
        existing_tank.photography = photography_json
        existing_tank.state = tank_data.state
        existing_tank.updated_at = datetime.now()
        
        db.commit()
        db.refresh(existing_tank)
        
        tank_response = TankResponse(
            id_tank=existing_tank.id_tank,
            name=existing_tank.name,
            latitude=tank_data.latitude,
            longitude=tank_data.longitude,
            connections=existing_tank.connections,
            photos=photos_to_store,
            photography=photos_to_store[0] if photos_to_store else None,
            state=existing_tank.state,
            created_at=existing_tank.created_at,
            updated_at=existing_tank.updated_at
        )
        
        return success_response(tank_response.model_dump(mode="json"))
    except Exception as e:
        db.rollback()
        return error_response(f"Error al actualizar el tanque: {str(e)}", 500)
    
@router.delete('/{tank_id}')
async def delete_tank(
    tank_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    existing_tank = db.query(Tank).filter(Tank.id_tank == tank_id).first()
    if not existing_tank:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El tanque no existe"),
            headers={"X-Error": "El tanque no existe"}
        )

    try:
        # Cambiar el estado a False (eliminación lógica)
        existing_tank.state = False
        existing_tank.updated_at = datetime.now()
        db.commit()
        db.refresh(existing_tank)
        return success_response({"detail": "Tanque desactivado correctamente"})
    except Exception as e:
        db.rollback()
        return error_response(f"Error al desactivar el tanque: {str(e)}", 500)