from fastapi import HTTPException
from app.models.bombs.bombs import Bombs
from typing import List, Optional
from datetime import datetime
from app.schemas.bombs.bombs import BombsBase, BombsResponse, BombsUpdate # Importar los esquemas de Bombs
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.utils.response import existence_response_dict
from app.utils.logger import create_log
from app.schemas.user.user import UserLogin


def get_all(db: Session, page: int, limit: int, search: Optional[str] = None):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")

    offset = (page - 1) * limit
    
    # Construir query base con coordenadas
    query = db.query(
        Bombs,
        func.ST_X(Bombs.coordinates).label('longitude'),
        func.ST_Y(Bombs.coordinates).label('latitude')
    )
    
    # Aplicar búsqueda si se proporciona
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Bombs.name).like(search_term),
                # El modelo Bombs no tiene un campo 'connections' por defecto, 
                # asumo que lo tiene o usamos el que has pasado en el modelo Tank
                func.lower(func.coalesce(Bombs.connections, '')).like(search_term) 
            )
        )
    
    # Contar total antes de paginar
    total = query.count()
    
    # Aplicar paginación
    bombs = query.order_by(Bombs.id_bombs.desc()).offset(offset).limit(limit).all()

    if not bombs and not search:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "No hay bombas disponibles"),
            headers={"X-Error": "No hay bombas disponibles"}
        )

    bomb_list = [
        {
            "id_bombs": t.id_bombs, 
            "name": t.name,
            "latitude": lat,
            "longitude": lon,
            "connections": t.connections,
            "photography": list(t.photography or []),
            "sector_id": t.sector_id,
            "active": t.active,
            "created_at": t.created_at,
            "updated_at": t.updated_at
        }
        for t, lon, lat in bombs
    ]

    return bomb_list, total


def get_by_id(db: Session, bomb_id: int):
    result = db.query(
        Bombs,
        func.ST_X(Bombs.coordinates).label('longitude'),
        func.ST_Y(Bombs.coordinates).label('latitude')
    ).filter(Bombs.id_bombs == bomb_id).first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "La bomba no existe"),
            headers={"X-Error": "La bomba no existe"}
        )

    bomb, longitude, latitude = result

    bomb_dict = {
        "id_bombs": bomb.id_bombs,
        "name": bomb.name,
        "latitude": latitude,
        "longitude": longitude,
        "connections": bomb.connections,
        "photography": list(bomb.photography or []),
        "sector_id": bomb.sector_id,
        "active": bomb.active,
        "created_at": bomb.created_at,
        "updated_at": bomb.updated_at
    }
    
    return bomb_dict

def create(db: Session, bomb_data: BombsBase, current_user: UserLogin):
    existing_bomb = db.query(Bombs).filter(Bombs.name == bomb_data.name).first()
    if existing_bomb:
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "La bomba ya existe"),
            headers={"X-Error": "La bomba ya existe"}
        )
    try:
        new_bomb = Bombs(
            name=bomb_data.name, 
            coordinates=f"SRID=4326;POINT({bomb_data.longitude} {bomb_data.latitude})",
            connections=bomb_data.connections,
            photography=bomb_data.photography if bomb_data.photography else [],
            sector_id=bomb_data.sector_id,
            active=bomb_data.active,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(new_bomb)
        db.commit()
        db.refresh(new_bomb)

        longitude, latitude = db.query(
            func.ST_X(new_bomb.coordinates),
            func.ST_Y(new_bomb.coordinates)
        ).first()

        bomb_dict = {
            "id_bombs": new_bomb.id_bombs,
            "name": new_bomb.name,
            "latitude": latitude,
            "longitude": longitude,
            "connections": new_bomb.connections,
            "photography": list(new_bomb.photography) if new_bomb.photography else [],
            "sector_id": new_bomb.sector_id,
            "active": new_bomb.active,
            "created_at": new_bomb.created_at,
            "updated_at": new_bomb.updated_at
        }
        create_log(
            db,
            user_id=current_user.id_user,
            action = "CREATE",
            entity = "Bomb",
            entity_id=new_bomb.id_bombs,
            description=f"El usuario {current_user.user} creó la bomba {new_bomb.name}"
        ) 
        return bomb_dict

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear la bomba: {str(e)}"
        )


def update(db: Session, bomb_id: int, bomb_data: BombsUpdate, current_user: UserLogin):
    bomb = db.query(Bombs).filter(Bombs.id_bombs == bomb_id).first()

    if not bomb:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "La bomba no existe"),
            headers={"X-Error": "La bomba no existe"}
        )

    try:
        # Usamos model_dump() y exclude_unset=True para actualizar solo los campos enviados
        update_data = bomb_data.model_dump(exclude_unset=True)

        if "latitude" in update_data and "longitude" in update_data:
            bomb.coordinates = f"SRID=4326;POINT({update_data['longitude']} {update_data['latitude']})"
            update_data.pop("latitude", None)
            update_data.pop("longitude", None)

        for field, value in update_data.items():
            setattr(bomb, field, value)

        bomb.updated_at = datetime.now()

        db.commit()
        db.refresh(bomb)

        longitude, latitude = db.query(
            func.ST_X(bomb.coordinates),
            func.ST_Y(bomb.coordinates)
        ).first()

        bomb_dict = {
            "id_bombs": bomb.id_bombs,
            "name": bomb.name,
            "latitude": latitude,
            "longitude": longitude,
            "connections": bomb.connections,
            "photography": list(bomb.photography) if bomb.photography else [],
            "sector_id": bomb.sector_id,
            "active": bomb.active,
            "created_at": bomb.created_at,
            "updated_at": bomb.updated_at
        }
        create_log(
            db,
            user_id=current_user.id_user,
            action = "UPDATE",
            entity = "Bomb",
            entity_id=bomb.id_bombs,
            description=f"El usuario {current_user.user} actualizó la bomba {bomb.name}"
        ) 
        return bomb_dict

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar la bomba: {str(e)}"
        )


def toggle_state(db: Session, bomb_id: int, current_user: UserLogin):
    bomb = db.query(Bombs).filter(Bombs.id_bombs == bomb_id).first()

    if not bomb:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "La bomba no existe"),
            headers={"X-Error": "La bomba no existe"}
        )

    bomb.active = not bomb.active
    bomb.updated_at = datetime.now()

    db.commit()
    db.refresh(bomb)
    
    status = "inactivo" if bomb.active is False else "activo"
    
    create_log(
        db,
        user_id=current_user.id_user,
        action = "TOGGLE",
        entity = "Bomb",
        entity_id=bomb.id_bombs,
        description=f"El usuario {current_user.user}, {status} la bomba {bomb.name}"
    ) 
    return bomb