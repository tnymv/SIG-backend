from fastapi import HTTPException, APIRouter
from app.models.pipes.pipes import Pipes
from app.models.tanks.tanks import Tank
from typing import List
from datetime import datetime
from app.schemas.pipes.pipes import PipesBase, PipesResponse,PipesResponseCreate, PipesUpdate, TankSimple
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.logger import create_log
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin
from sqlalchemy.orm import joinedload
from sqlalchemy import func

def get_all(db: Session, page: int, limit: int):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")

    offset = (page - 1) * limit
    pipes = db.query(
        Pipes,
        func.ST_X(Pipes.coordinates).label('longitude'),
        func.ST_Y(Pipes.coordinates).label('latitude')
    ).options(joinedload(Pipes.tanks)) \
     .offset(offset).limit(limit).all()

    if not pipes:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "No hay tuberías registradas"))

    result = []
    for pipe, lon, lat in pipes:
        result.append({
            "id_pipes": pipe.id_pipes,
            "material": pipe.material,
            "diameter": pipe.diameter,
            "status": pipe.status,
            "size": pipe.size,
            "installation_date": pipe.installation_date,
            "latitude": lat,
            "longitude": lon,
            "observations": pipe.observations,
            "created_at": pipe.created_at,
            "updated_at": pipe.updated_at,
            "tanks": [{"id_tank": t.id_tank, "name": t.name} for t in pipe.tanks]
        })

    return result


def get_by_id(db: Session, pipe_id: int):
    result = db.query(
        Pipes,
        func.ST_X(Pipes.coordinates).label('longitude'),
        func.ST_Y(Pipes.coordinates).label('latitude')
    ).options(joinedload(Pipes.tanks)) \
     .filter(Pipes.id_pipes == pipe_id).first()

    if not result:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "La tubería no existe"))

    pipe, lon, lat = result
    return {
        "id_pipes": pipe.id_pipes,
        "material": pipe.material,
        "diameter": pipe.diameter,
        "status": pipe.status,
        "size": pipe.size,
        "installation_date": pipe.installation_date,
        "latitude": lat,
        "longitude": lon,
        "observations": pipe.observations,
        "created_at": pipe.created_at,
        "updated_at": pipe.updated_at,
        "tanks": [{"id_tank": t.id_tank, "name": t.name} for t in pipe.tanks]
    }


def create(db: Session, pipe_data: PipesBase,current_user: UserLogin):
    existing = db.query(Pipes).filter(Pipes.material == pipe_data.material).first()
    if existing:
        raise HTTPException(status_code=409, detail=existence_response_dict(True, "La tubería ya existe"))

    try:
        new_pipe = Pipes(
            material=pipe_data.material,
            diameter=pipe_data.diameter,
            status=pipe_data.status,
            size=pipe_data.size,
            installation_date=pipe_data.installation_date,
            coordinates=f"SRID=4326;POINT({pipe_data.longitude} {pipe_data.latitude})",
            observations=pipe_data.observations,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        for tank_id in pipe_data.tank_ids:
            tank = db.query(Tank).filter(Tank.id_tank == tank_id).first()
            if tank:
                new_pipe.tanks.append(tank)

        db.add(new_pipe)
        db.commit()
        db.refresh(new_pipe)

        lon, lat = db.query(func.ST_X(new_pipe.coordinates), func.ST_Y(new_pipe.coordinates)).first()

        create_log(
                db,
                user_id=current_user.id_user,
                action = "CREATE",
                entity = "Pipes",
                entity_id=new_pipe.id_pipes,
                description=f"El usuario {current_user.user} creó la tuberia {new_pipe.id_pipes}"
            ) 
        return {
            "id_pipes": new_pipe.id_pipes,
            "material": new_pipe.material,
            "diameter": new_pipe.diameter,
            "status": new_pipe.status,
            "size": new_pipe.size,
            "installation_date": new_pipe.installation_date,
            "latitude": lat,
            "longitude": lon,
            "observations": new_pipe.observations,
            "created_at": new_pipe.created_at,
            "updated_at": new_pipe.updated_at,
            "tanks": [{"id_tank": t.id_tank, "name": t.name} for t in new_pipe.tanks]
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la tubería: {str(e)}")


def update(db: Session, pipe_id: int, pipe_data: PipesUpdate,current_user: UserLogin):
    pipe = db.query(Pipes).filter(Pipes.id_pipes == pipe_id).first()
    if not pipe:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "La tubería no existe"))

    try:
        data = pipe_data.dict(exclude_unset=True)

        if "latitude" in data and "longitude" in data:
            pipe.coordinates = f"SRID=4326;POINT({data['longitude']} {data['latitude']})"
            data.pop("latitude", None)
            data.pop("longitude", None)

        if "tank_ids" in data:
            pipe.tanks.clear()
            for tank_id in data["tank_ids"]:
                tank = db.query(Tank).filter(Tank.id_tank == tank_id).first()
                if tank:
                    pipe.tanks.append(tank)
            data.pop("tank_ids", None)

        for field, value in data.items():
            setattr(pipe, field, value)

        pipe.updated_at = datetime.now()
        db.commit()
        db.refresh(pipe)

        lon, lat = db.query(func.ST_X(pipe.coordinates), func.ST_Y(pipe.coordinates)).first()

        create_log(
            db,
            user_id=current_user.id_user,
            action = "UPDATE",
            entity = "Pipe",
            entity_id=pipe.id_pipes,
            description=f"El usuario {current_user.user} actualizo el permiso {pipe.id_pipes}"
        ) 
        return {
            "id_pipes": pipe.id_pipes,
            "material": pipe.material,
            "diameter": pipe.diameter,
            "status": pipe.status,
            "size": pipe.size,
            "installation_date": pipe.installation_date,
            "latitude": lat,
            "longitude": lon,
            "observations": pipe.observations,
            "created_at": pipe.created_at,
            "updated_at": pipe.updated_at,
            "tanks": [{"id_tank": t.id_tank, "name": t.name} for t in pipe.tanks]
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar la tubería: {str(e)}")


def toggle_state(db: Session, pipe_id: int,current_user: UserLogin):
    pipe = db.query(Pipes).filter(Pipes.id_pipes == pipe_id).first()
    if not pipe:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "La tubería no existe"))

    pipe.status = not pipe.status
    pipe.updated_at = datetime.now()

    db.commit()
    db.refresh(pipe)
    state = ""
    if pipe.status is False:
        state = "inactivo"
    else: 
        state = "activo" 
    create_log(
        db,
        user_id=current_user.id_user,
        action = "TOGGLE",
        entity = "Permission",
        entity_id=pipe.id_pipes,
        description=f"El usuario {current_user.user}, {state} el permiso {pipe.id_pipes}"
    ) 
    return pipe