from fastapi import HTTPException, APIRouter
from app.models.pipes.pipes import Pipes
from app.models.tanks.tanks import Tank
from app.models.connection.connections import Connection
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
    ).options(joinedload(Pipes.tanks), joinedload(Pipes.connections)) \
     .filter(Pipes.id_pipes == pipe_id).first()

    if not result:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "La tubería no existe"))

    pipe, geojson = result
    coords = json.loads(geojson)["coordinates"]
    
    # Obtener coordenadas de inicio y fin de la tubería (GeoJSON usa [lon, lat])
    start_coord = coords[0] if len(coords) > 0 else None
    end_coord = coords[-1] if len(coords) > 0 else None
    
    # Determinar qué conexiones son de inicio y fin basándose en las coordenadas
    start_connection_id = None
    end_connection_id = None
    
    # Si hay conexiones relacionadas, determinar cuál es inicio y cuál fin
    if pipe.connections:
        conn_list = list(pipe.connections)
        
        # Si hay exactamente 2 conexiones, asignarlas como inicio y fin
        if len(conn_list) == 2:
            # Intentar determinar por coordenadas si están disponibles
            if start_coord and end_coord:
                conn_data = []
                for conn in conn_list:
                    conn_lon = db.scalar(func.ST_X(conn.coordenates))
                    conn_lat = db.scalar(func.ST_Y(conn.coordenates))
                    conn_data.append({
                        'id': conn.id_connection,
                        'lon': conn_lon,
                        'lat': conn_lat
                    })
                
                # Calcular distancias a puntos de inicio y fin
                distances = []
                for conn in conn_data:
                    start_dist = ((conn['lon'] - start_coord[0]) ** 2 + (conn['lat'] - start_coord[1]) ** 2) ** 0.5
                    end_dist = ((conn['lon'] - end_coord[0]) ** 2 + (conn['lat'] - end_coord[1]) ** 2) ** 0.5
                    distances.append({
                        'id': conn['id'],
                        'start_dist': start_dist,
                        'end_dist': end_dist
                    })
                
                # Asignar la más cercana al inicio como start, la más cercana al fin como end
                if distances[0]['start_dist'] < distances[1]['start_dist']:
                    start_connection_id = distances[0]['id']
                    end_connection_id = distances[1]['id']
                else:
                    start_connection_id = distances[1]['id']
                    end_connection_id = distances[0]['id']
            else:
                # Si no hay coordenadas, asignar directamente
                start_connection_id = conn_list[0].id_connection
                end_connection_id = conn_list[1].id_connection
        elif len(conn_list) == 1:
            # Si solo hay una conexión, asignarla como inicio
            start_connection_id = conn_list[0].id_connection

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
        "tanks": [{"id_tank": t.id_tank, "name": t.name} for t in pipe.tanks],
        "start_connection_id": start_connection_id,
        "end_connection_id": end_connection_id,
        "connections": [{"id_connection": c.id_connection} for c in pipe.connections]
    }


def create(db: Session, pipe_data: PipesBase, current_user: UserLogin):
    existing = db.query(Pipes).filter(Pipes.material == pipe_data.material).first()
    if existing:
        raise HTTPException(status_code=409, detail=existence_response_dict(True, "La tubería ya existe"))

    try:
        # Validar que coordinates tenga exactamente 2 puntos
        if len(pipe_data.coordinates) != 2:
            raise HTTPException(status_code=400, detail="Las coordenadas deben tener exactamente 2 puntos (inicio y fin)")

        # Obtener coordenadas de conexiones si se proporcionan
        final_coordinates = list(pipe_data.coordinates)
        
        # Si hay start_connection_id, obtener sus coordenadas
        if pipe_data.start_connection_id:
            start_conn = db.query(Connection).filter(Connection.id_connection == pipe_data.start_connection_id).first()
            if not start_conn:
                raise HTTPException(status_code=404, detail="La conexión de inicio no existe")
            start_lon = db.scalar(func.ST_X(start_conn.coordenates))
            start_lat = db.scalar(func.ST_Y(start_conn.coordenates))
            final_coordinates[0] = (start_lon, start_lat)
        
        # Si hay end_connection_id, obtener sus coordenadas
        if pipe_data.end_connection_id:
            end_conn = db.query(Connection).filter(Connection.id_connection == pipe_data.end_connection_id).first()
            if not end_conn:
                raise HTTPException(status_code=404, detail="La conexión de fin no existe")
            end_lon = db.scalar(func.ST_X(end_conn.coordenates))
            end_lat = db.scalar(func.ST_Y(end_conn.coordenates))
            final_coordinates[1] = (end_lon, end_lat)

        # Construir LINESTRING con los 2 puntos
        coords_text = ", ".join([f"{lon} {lat}" for lon, lat in final_coordinates])

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

        # Asociar tanques
        for tank_id in pipe_data.tank_ids:
            tank = db.query(Tank).filter(Tank.id_tank == tank_id).first()
            if tank:
                new_pipe.tanks.append(tank)

        # Asociar conexiones si se proporcionaron
        if pipe_data.start_connection_id:
            start_conn = db.query(Connection).filter(Connection.id_connection == pipe_data.start_connection_id).first()
            if start_conn:
                new_pipe.connections.append(start_conn)
        
        if pipe_data.end_connection_id:
            end_conn = db.query(Connection).filter(Connection.id_connection == pipe_data.end_connection_id).first()
            if end_conn:
                # Evitar duplicados si start y end son la misma conexión
                if end_conn not in new_pipe.connections:
                    new_pipe.connections.append(end_conn)

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
            "coordinates": final_coordinates
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la tubería: {str(e)}")



def update(db: Session, pipe_id: int, pipe_data: PipesUpdate, current_user: UserLogin):
    pipe = db.query(Pipes).filter(Pipes.id_pipes == pipe_id).first()
    if not pipe:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "La tubería no existe"))

    try:
        data = pipe_data.dict(exclude_unset=True)

        # Obtener coordenadas actuales si no se proporcionan nuevas
        current_coords = None
        if "coordinates" not in data:
            geometry = db.query(func.ST_AsGeoJSON(Pipes.coordinates).label("geometry")) \
                .filter(Pipes.id_pipes == pipe_id) \
                .scalar()
            if geometry:
                current_coords = json.loads(geometry)["coordinates"]
        
        # Manejar coordenadas y conexiones
        final_coordinates = data.get("coordinates", current_coords)
        
        # Si se proporcionan connection_ids, obtener sus coordenadas
        if "start_connection_id" in data and data["start_connection_id"]:
            start_conn = db.query(Connection).filter(Connection.id_connection == data["start_connection_id"]).first()
            if not start_conn:
                raise HTTPException(status_code=404, detail="La conexión de inicio no existe")
            start_lon = db.scalar(func.ST_X(start_conn.coordenates))
            start_lat = db.scalar(func.ST_Y(start_conn.coordenates))
            if final_coordinates:
                final_coordinates[0] = (start_lon, start_lat)
            else:
                # Si no hay coordenadas actuales, necesitamos obtener el punto final
                geometry = db.query(func.ST_AsGeoJSON(Pipes.coordinates).label("geometry")) \
                    .filter(Pipes.id_pipes == pipe_id) \
                    .scalar()
                if geometry:
                    current_coords = json.loads(geometry)["coordinates"]
                    final_coordinates = [(start_lon, start_lat), current_coords[1] if len(current_coords) > 1 else (start_lon, start_lat)]
        
        if "end_connection_id" in data and data["end_connection_id"]:
            end_conn = db.query(Connection).filter(Connection.id_connection == data["end_connection_id"]).first()
            if not end_conn:
                raise HTTPException(status_code=404, detail="La conexión de fin no existe")
            end_lon = db.scalar(func.ST_X(end_conn.coordenates))
            end_lat = db.scalar(func.ST_Y(end_conn.coordenates))
            if final_coordinates:
                final_coordinates[1] = (end_lon, end_lat)
            else:
                # Si no hay coordenadas actuales, necesitamos obtener el punto inicial
                geometry = db.query(func.ST_AsGeoJSON(Pipes.coordinates).label("geometry")) \
                    .filter(Pipes.id_pipes == pipe_id) \
                    .scalar()
                if geometry:
                    current_coords = json.loads(geometry)["coordinates"]
                    final_coordinates = [current_coords[0] if len(current_coords) > 0 else (end_lon, end_lat), (end_lon, end_lat)]

        # Validar que tengamos exactamente 2 puntos
        if final_coordinates and len(final_coordinates) != 2:
            raise HTTPException(status_code=400, detail="Las coordenadas deben tener exactamente 2 puntos (inicio y fin)")

        # Actualizar coordenadas si hay cambios
        if final_coordinates:
            coords_text = ", ".join([f"{lon} {lat}" for lon, lat in final_coordinates])
            pipe.coordinates = WKTElement(f"LINESTRING({coords_text})", srid=4326)
            data.pop("coordinates", None)

        # Actualizar tanques
        if "tank_ids" in data:
            pipe.tanks.clear()
            for tank_id in data["tank_ids"]:
                tank = db.query(Tank).filter(Tank.id_tank == tank_id).first()
                if tank:
                    pipe.tanks.append(tank)
            data.pop("tank_ids", None)

        # Actualizar conexiones si se proporcionan
        if "start_connection_id" in data or "end_connection_id" in data:
            pipe.connections.clear()
            if "start_connection_id" in data and data["start_connection_id"]:
                start_conn = db.query(Connection).filter(Connection.id_connection == data["start_connection_id"]).first()
                if start_conn:
                    pipe.connections.append(start_conn)
            if "end_connection_id" in data and data["end_connection_id"]:
                end_conn = db.query(Connection).filter(Connection.id_connection == data["end_connection_id"]).first()
                if end_conn:
                    # Evitar duplicados si start y end son la misma conexión
                    if end_conn not in pipe.connections:
                        pipe.connections.append(end_conn)
            data.pop("start_connection_id", None)
            data.pop("end_connection_id", None)

        # Actualizar otros campos
        for field, value in data.items():
            setattr(pipe, field, value)

        pipe.updated_at = datetime.now()
        db.commit()
        db.refresh(pipe)

        # Obtener coordenadas actualizadas en formato GeoJSON
        geometry = db.query(func.ST_AsGeoJSON(Pipes.coordinates).label("geometry")) \
            .filter(Pipes.id_pipes == pipe.id_pipes) \
            .scalar()
        coords = json.loads(geometry)["coordinates"] if geometry else []

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
            "coordinates": coords,
            "observations": pipe.observations,
            "created_at": pipe.created_at,
            "updated_at": pipe.updated_at,
            "tanks": [{"id_tank": t.id_tank, "name": t.name} for t in pipe.tanks]
        }

    except HTTPException:
        raise
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