from fastapi import HTTPException, APIRouter
from app.models.tanks.tanks import Tank
from typing import List
from datetime import datetime
from app.schemas.tanks.tanks import TankBase, TankResponse, TankUpdate
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.utils.response import existence_response_dict
from app.utils.logger import create_log
from sqlalchemy import func
from app.schemas.user.user import UserLogin


def get_all(db: Session, page: int, limit: int):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")

    offset = (page - 1) * limit
    
    query = db.query(Tank)
    total = query.count()
    
    tanks = db.query(
        Tank,
        func.ST_X(Tank.coordinates).label('longitude'),
        func.ST_Y(Tank.coordinates).label('latitude')
    ).offset(offset).limit(limit).all()

    if not tanks:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "No hay tanques disponibles"),
            headers={"X-Error": "No hay tanques disponibles"}
        )

    tank_list = [
        {
            "id_tank": t.id_tank,
            "name": t.name,
            "latitude": lat,
            "longitude": lon,
            "connections": t.connections,
            "photography": list(t.photography or []),
            "state": t.state,
            "created_at": t.created_at,
            "updated_at": t.updated_at
        }
        for t, lon, lat in tanks
    ]

    return tank_list, total


def get_by_id(db: Session, tank_id: int):
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

    tank_dict = {
        "id_tank": tank.id_tank,
        "name": tank.name,
        "latitude": latitude,
        "longitude": longitude,
        "connections": tank.connections,
        "photography": list(tank.photography or []),
        "state": tank.state,
        "created_at": tank.created_at,
        "updated_at": tank.updated_at
    }
    
    return tank_dict

def create(db: Session, tank_data: TankBase,current_user: UserLogin):
    existing_tank = db.query(Tank).filter(Tank.name == tank_data.name).first()
    if existing_tank:
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

        longitude, latitude = db.query(
            func.ST_X(new_tank.coordinates),
            func.ST_Y(new_tank.coordinates)
        ).first()

        tank_dict = {
            "id_tank": new_tank.id_tank,
            "name": new_tank.name,
            "latitude": latitude,
            "longitude": longitude,
            "connections": new_tank.connections,
            "photography": list(new_tank.photography) if new_tank.photography else [],
            "state": new_tank.state,
            "created_at": new_tank.created_at,
            "updated_at": new_tank.updated_at
        }
        create_log(
            db,
            user_id=current_user.id_user,
            action = "CREATE",
            entity = "Tank",
            entity_id=new_tank.id_tank,
            description=f"El usuario {current_user.user} creó el tanque {new_tank.name}"
        ) 
        return tank_dict

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el tanque: {str(e)}"
        )


def update(db: Session, tank_id: int, tank_data: TankUpdate,current_user: UserLogin):
    tank = db.query(Tank).filter(Tank.id_tank == tank_id).first()

    if not tank:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El tanque no existe"),
            headers={"X-Error": "El tanque no existe"}
        )

    try:
        update_data = tank_data.dict(exclude_unset=True)

        if "latitude" in update_data and "longitude" in update_data:
            tank.coordinates = f"SRID=4326;POINT({update_data['longitude']} {update_data['latitude']})"
            update_data.pop("latitude", None)
            update_data.pop("longitude", None)

        for field, value in update_data.items():
            setattr(tank, field, value)

        tank.updated_at = datetime.now()

        db.commit()
        db.refresh(tank)

        longitude, latitude = db.query(
            func.ST_X(tank.coordinates),
            func.ST_Y(tank.coordinates)
        ).first()

        tank_dict = {
            "id_tank": tank.id_tank,
            "name": tank.name,
            "latitude": latitude,
            "longitude": longitude,
            "connections": tank.connections,
            "photography": list(tank.photography) if tank.photography else [],
            "state": tank.state,
            "created_at": tank.created_at,
            "updated_at": tank.updated_at
        }
        create_log(
            db,
            user_id=current_user.id_user,
            action = "UPDATE",
            entity = "Tank",
            entity_id=tank.id_tank,
            description=f"El usuario {current_user.user} actualizo el tanque {tank.name}"
        ) 
        return tank_dict

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar el tanque: {str(e)}"
        )


def toggle_state(db: Session, tank_id: int,current_user: UserLogin):
    tank = db.query(Tank).filter(Tank.id_tank == tank_id).first()

    if not tank:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El tanque no existe"),
            headers={"X-Error": "El tanque no existe"}
        )

    tank.state = not tank.state
    tank.updated_at = datetime.now()

    db.commit()
    db.refresh(tank)
    status = ""
    if tank.state is False:
        status = "inactivo"
    else: 
        status = "activo" 
    create_log(
        db,
        user_id=current_user.id_user,
        action = "TOGGLE",
        entity = "Tank",
        entity_id=tank.id_tank,
        description=f"El usuario {current_user.user}, {status} el permiso {tank.name}"
    ) 
    return tank
