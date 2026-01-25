from fastapi import HTTPException
from app.models.gate_valve.gate_valve import Gate_Valve # Asegura esta ruta
from typing import List, Optional
from datetime import datetime
from app.schemas.gate_valve.gate_valve import Gate_valveBase, Gate_valveResponse, Gate_valveUpdate
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.utils.response import existence_response_dict
from app.utils.logger import create_log
from app.schemas.user.user import UserLogin

def get_all(db: Session, page: int, limit: int, search: Optional[str] = None):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")

    offset = (page - 1) * limit
    
    # Query base extrayendo latitud y longitud de la geometría
    query = db.query(
        Gate_Valve,
        func.ST_X(Gate_Valve.coordinates).label('longitude'),
        func.ST_Y(Gate_Valve.coordinates).label('latitude')
    )
    
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Gate_Valve.name).like(search_term),
                func.lower(func.coalesce(Gate_Valve.material, '')).like(search_term)
            )
        )
    
    total = query.count()
    valves = query.order_by(Gate_Valve.id_gate_valve.desc()).offset(offset).limit(limit).all()

    if not valves and not search:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "No hay válvulas de compuerta disponibles"),
            headers={"X-Error": "No hay válvulas disponibles"}
        )

    valve_list = [
        {
            "id_gate_valve": v.id_gate_valve,
            "name": v.name,
            "latitude": lat,
            "longitude": lon,
            "material": v.material,
            "diameter": v.diameter,
            "photography": list(v.photography or []),
            "sector_id": v.sector_id,
            "active": v.active,
            "created_at": v.created_at,
            "updated_at": v.updated_at
        }
        for v, lon, lat in valves
    ]

    return valve_list, total

def get_by_id(db: Session, valve_id: int):
    result = db.query(
        Gate_Valve,
        func.ST_X(Gate_Valve.coordinates).label('longitude'),
        func.ST_Y(Gate_Valve.coordinates).label('latitude')
    ).filter(Gate_Valve.id_gate_valve == valve_id).first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "La válvula no existe"),
            headers={"X-Error": "La válvula no existe"}
        )

    valve, longitude, latitude = result

    return {
        "id_gate_valve": valve.id_gate_valve,
        "name": valve.name,
        "latitude": latitude,
        "longitude": longitude,
        "material": valve.material,
        "diameter": valve.diameter,
        "photography": list(valve.photography or []),
        "sector_id": valve.sector_id,
        "active": valve.active,
        "created_at": valve.created_at,
        "updated_at": valve.updated_at
    }

def create(db: Session, valve_data: Gate_valveBase, current_user: UserLogin):
    existing = db.query(Gate_Valve).filter(Gate_Valve.name == valve_data.name).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "La válvula ya existe"),
            headers={"X-Error": "La válvula ya existe"}
        )
    try:
        new_valve = Gate_Valve(
            name=valve_data.name, 
            coordinates=f"SRID=4326;POINT({valve_data.longitude} {valve_data.latitude})",
            material=valve_data.material,
            diameter=valve_data.diameter,
            photography=valve_data.photography if valve_data.photography else [],
            sector_id=valve_data.sector_id,
            active=valve_data.active,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_valve)
        db.commit()
        db.refresh(new_valve)

        # Obtenemos coordenadas para la respuesta
        lon, lat = db.query(
            func.ST_X(new_valve.coordinates),
            func.ST_Y(new_valve.coordinates)
        ).first()

        create_log(
            db,
            user_id=current_user.id_user,
            action="CREATE",
            entity="Gate_Valve",
            entity_id=new_valve.id_gate_valve,
            description=f"El usuario {current_user.user} creó la válvula {new_valve.name}"
        ) 

        return {**get_by_id(db, new_valve.id_gate_valve)}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la válvula: {str(e)}")

def update(db: Session, valve_id: int, valve_data: Gate_valveUpdate, current_user: UserLogin):
    valve = db.query(Gate_Valve).filter(Gate_Valve.id_gate_valve == valve_id).first()

    if not valve:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "La válvula no existe"),
            headers={"X-Error": "La válvula no existe"}
        )

    try:
        update_data = valve_data.dict(exclude_unset=True)

        if "latitude" in update_data or "longitude" in update_data:
            # Si solo viene uno, usamos el valor actual del otro para no romper la geometría
            current_lon, current_lat = db.query(func.ST_X(valve.coordinates), func.ST_Y(valve.coordinates)).first()
            new_lon = update_data.get("longitude", current_lon)
            new_lat = update_data.get("latitude", current_lat)
            valve.coordinates = f"SRID=4326;POINT({new_lon} {new_lat})"
            update_data.pop("latitude", None)
            update_data.pop("longitude", None)

        for field, value in update_data.items():
            setattr(valve, field, value)

        valve.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(valve)

        create_log(
            db,
            user_id=current_user.id_user,
            action="UPDATE",
            entity="Gate_Valve",
            entity_id=valve.id_gate_valve,
            description=f"El usuario {current_user.user} actualizó la válvula {valve.name}"
        ) 
        return get_by_id(db, valve.id_gate_valve)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar la válvula: {str(e)}")

def toggle_state(db: Session, valve_id: int, current_user: UserLogin):
    valve = db.query(Gate_Valve).filter(Gate_Valve.id_gate_valve == valve_id).first()

    if not valve:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "La válvula no existe"))

    valve.active = not valve.active
    valve.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(valve)
    
    status = "activo" if valve.active else "inactivo"
    create_log(
        db,
        user_id=current_user.id_user,
        action="TOGGLE",
        entity="Gate_Valve",
        entity_id=valve.id_gate_valve,
        description=f"El usuario {current_user.user} cambió el estado de la válvula {valve.name} a {status}"
    ) 
    return valve