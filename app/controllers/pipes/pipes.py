from fastapi import HTTPException, APIRouter
from app.models.pipes.pipes import Pipes
from app.models.tanks.tanks import Tank
from typing import List, Optional
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
from sqlalchemy import func, or_
import json
from geoalchemy2 import WKTElement

def get_all(db: Session, page: int, limit: int, search: Optional[str] = None):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")

    offset = (page - 1) * limit
    
    # Construir query base con coordenadas
    query = db.query(
        Pipes,
        func.ST_AsGeoJSON(Pipes.coordinates).label("geometry")
    ).options(joinedload(Pipes.tanks))
    
    # Aplicar búsqueda si se proporciona
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Pipes.material).like(search_term),
                func.lower(func.coalesce(Pipes.observations, '')).like(search_term)
            )
        )
    
    # Contar total antes de paginar (necesitamos una query separada para el count)
    count_query = db.query(Pipes)
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        count_query = count_query.filter(
            or_(
                func.lower(Pipes.material).like(search_term),
                func.lower(func.coalesce(Pipes.observations, '')).like(search_term)
            )
        )
    total = count_query.count()
    
    # Aplicar paginación
    pipes = query.offset(offset).limit(limit).all()

    # Si no hay resultados pero hay búsqueda, no es un error, solo no hay coincidencias
    if not pipes and not search:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "No hay tuberías registradas"))

    result = []
    for pipe, geojson in pipes:
        coords = json.loads(geojson)["coordinates"]
        result.append({
            "id_pipes": pipe.id_pipes,
            "material": pipe.material,
            "diameter": pipe.diameter,
            "status": pipe.status,
            "size": pipe.size,
            "installation_date": pipe.installation_date,
            "coordinates": coords,
            "observations": pipe.observations,
            "created_at": pipe.created_at,
            "updated_at": pipe.updated_at,
            "tanks": [{"id_tank": t.id_tank, "name": t.name} for t in pipe.tanks]
        })

    return result, total

def get_by_id(db: Session, pipe_id: int):
    result = db.query(
        Pipes,
        func.ST_AsGeoJSON(Pipes.coordinates).label("geometry")
    ).options(joinedload(Pipes.tanks)) \
     .filter(Pipes.id_pipes == pipe_id).first()

    if not result:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "La tubería no existe"))

    pipe, geojson = result
    coords = json.loads(geojson)["coordinates"]

    return {
        "id_pipes": pipe.id_pipes,
        "material": pipe.material,
        "diameter": pipe.diameter,
        "status": pipe.status,
        "size": pipe.size,
        "installation_date": pipe.installation_date,
        "coordinates": coords,  # 🔹 devuelve toda la línea
        "observations": pipe.observations,
        "created_at": pipe.created_at,
        "updated_at": pipe.updated_at,
        "tanks": [{"id_tank": t.id_tank, "name": t.name} for t in pipe.tanks]
    }


def create(db: Session, pipe_data: PipesBase, current_user: UserLogin):
    existing = db.query(Pipes).filter(Pipes.material == pipe_data.material).first()
    if existing:
        raise HTTPException(status_code=409, detail=existence_response_dict(True, "La tubería ya existe"))

    try:
        coords_text = ", ".join([f"{lon} {lat}" for lon, lat in pipe_data.coordinates])

        new_pipe = Pipes(
        material=pipe_data.material,
        diameter=pipe_data.diameter,
        status=pipe_data.status,
        size=pipe_data.size,
        installation_date=pipe_data.installation_date,
        coordinates=WKTElement(f"LINESTRING({coords_text})", srid=4326),
        observations=pipe_data.observations,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
        )   

        for tank_id in pipe_data.tank_ids:
            tank = db.query(Tank).filter(Tank.id_tank == tank_id).first()
            if tank:
                new_pipe.tanks.append(tank)

        db.add(new_pipe)
        db.commit()
        db.refresh(new_pipe)

        create_log(
            db,
            user_id=current_user.id_user,
            action="CREATE",
            entity="Pipes",
            entity_id=new_pipe.id_pipes,
            description=f"El usuario {current_user.user} creó la tubería {new_pipe.id_pipes}"
        )

        return {
            "id_pipes": new_pipe.id_pipes,
            "material": new_pipe.material,
            "diameter": new_pipe.diameter,
            "status": new_pipe.status,
            "size": new_pipe.size,
            "installation_date": new_pipe.installation_date,
            "observations": new_pipe.observations,
            "created_at": new_pipe.created_at,
            "updated_at": new_pipe.updated_at,
            "tanks": [{"id_tank": t.id_tank, "name": t.name} for t in new_pipe.tanks],
            "coordinates": pipe_data.coordinates
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la tubería: {str(e)}")



def update(db: Session, pipe_id: int, pipe_data: PipesUpdate, current_user: UserLogin):
    pipe = db.query(Pipes).filter(Pipes.id_pipes == pipe_id).first()
    if not pipe:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "La tubería no existe"))

    try:
        data = pipe_data.dict(exclude_unset=True)

        if "coordinates" in data:
            coords_text = ", ".join([f"{lon} {lat}" for lon, lat in data["coordinates"]])
            pipe.coordinates = f"SRID=4326;LINESTRING({coords_text})"
            data.pop("coordinates", None)

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

        create_log(
            db,
            user_id=current_user.id_user,
            action="UPDATE",
            entity="Pipe",
            entity_id=pipe.id_pipes,
            description=f"El usuario {current_user.user} actualizó la tubería {pipe.id_pipes}"
        )

        return {
            "id_pipes": pipe.id_pipes,
            "material": pipe.material,
            "diameter": pipe.diameter,
            "status": pipe.status,
            "size": pipe.size,
            "installation_date": pipe.installation_date,
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
        action="TOGGLE",
        entity="Pipes",
        entity_id=pipe.id_pipes,
        description=f"El usuario {current_user.user} cambió el estado de la tubería {pipe.id_pipes} a {state}"
    )

    return pipe