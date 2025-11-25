from fastapi import HTTPException, APIRouter
from app.models.tanks.tanks import Tank
from app.models.connection.connections import Connection
from app.models.pipes.pipes import Pipes
from typing import List
from datetime import datetime
from app.schemas.map.map import ConnectionSchema, PipeSchema, TankSchema
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.utils.response import existence_response_dict
from app.utils.logger import create_log
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.schemas.user.user import UserLogin
from sqlalchemy import func
from app.models.interventions.interventions import Interventions
from app.models.intervention_entities.intervention_entities import Intervention_entities
import json


def get_all_tank_with_pipes_and_connections(db: Session) -> List[TankSchema]:
    tanks = (
        db.query(Tank)
        .options(
            joinedload(Tank.pipes).joinedload(Pipes.connections)
        )
        .filter(Tank.active == True)   # <-- SOLO TANQUES ACTIVOS
        .all()
    )

    if not tanks:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "No hay tanques activos"),
            headers={"X-Error": "No hay tanques activos"}
        )

    # Filtrar tuberías activas
    for tank in tanks:
        tank.pipes = [pipe for pipe in tank.pipes if pipe.active == True]

    # Filtrar conexiones activas
    for tank in tanks:
        for pipe in tank.pipes:
            pipe.connections = [
                conn for conn in pipe.connections if conn.active == True
            ]

    # IDs después de filtrar
    all_pipe_ids = list(set(
        pipe.id_pipes
        for tank in tanks
        for pipe in tank.pipes
    ))

    pipe_coords_map = {}

    if all_pipe_ids:
        pipe_coords_query = db.query(
            Pipes.id_pipes,
            func.ST_AsText(Pipes.coordinates)
        ).filter(Pipes.id_pipes.in_(all_pipe_ids)).all()

        pipe_coords_map = {pid: coords_text for pid, coords_text in pipe_coords_query}

    all_conn_ids = list(set(
        conn.id_connection
        for tank in tanks
        for pipe in tank.pipes
        for conn in pipe.connections
    ))

    conn_coords_map = {}

    if all_conn_ids:
        conn_coords_query = db.query(
            Connection.id_connection,
            func.ST_X(Connection.coordenates).label("longitude"),
            func.ST_Y(Connection.coordenates).label("latitude")
        ).filter(
            Connection.id_connection.in_(all_conn_ids)
        ).filter(
            Connection.active == True      # <-- SOLO CONEXIONES ACTIVAS (opcional)
        ).all()

        conn_coords_map = {cid: (lon, lat) for cid, lon, lat in conn_coords_query}

    # Construcción final
    tank_list = []

    for tank in tanks:
        tank_lon = db.scalar(func.ST_X(tank.coordinates))
        tank_lat = db.scalar(func.ST_Y(tank.coordinates))

        pipes_data = []

        for pipe in tank.pipes:
            pipe_coords_text = pipe_coords_map.get(pipe.id_pipes, "LINESTRING()")

            coords = []
            if pipe_coords_text and pipe_coords_text != "LINESTRING()":
                coords_str = pipe_coords_text.replace("LINESTRING(", "").replace(")", "")
                if coords_str:
                    coords = [
                        tuple(map(float, c.strip().split()))
                        for c in coords_str.split(",")
                        if c.strip()
                    ]

            connections_data = []
            for conn in pipe.connections:
                lon_conn, lat_conn = conn_coords_map.get(conn.id_connection, (0.0, 0.0))

                connections_data.append(
                    ConnectionSchema(
                        id_connection=conn.id_connection,
                        latitude=lat_conn,
                        longitude=lon_conn,
                        material=conn.material or "",
                        pressure_nominal=conn.pressure_nominal or "",
                        connection_type=conn.connection_type or "",
                        depth_m=float(conn.depth_m) if conn.depth_m else 0.0,
                        installed_by=conn.installed_by or "",
                        active=conn.active
                    )
                )

            pipes_data.append(
                PipeSchema(
                    id_pipes=pipe.id_pipes,
                    material=pipe.material,
                    diameter=pipe.diameter,
                    active=pipe.active,
                    size=pipe.size,
                    installation_date=pipe.installation_date,
                    coordinates=coords,
                    observations=pipe.observations or "",
                    connections=connections_data
                )
            )

        tank_list.append(
            TankSchema(
                id_tank=tank.id_tank,
                name=tank.name,
                latitude=tank_lat,
                longitude=tank_lon,
                photography=list(tank.photography or []),
                active=tank.active,
                pipes=pipes_data
            )
        )

    return tank_list

def get_interventions_in_range(db: Session, start_date, end_date):

    interventions = (
        db.query(Interventions)
        .filter(Interventions.start_date >= start_date)
        .filter(Interventions.end_date <= end_date)
        .options(
            joinedload(Interventions.entities).joinedload(Intervention_entities.tank),
            joinedload(Interventions.entities).joinedload(Intervention_entities.pipe),
            joinedload(Interventions.entities).joinedload(Intervention_entities.connection)
        )
        .all()
    )

    results = []

    for intervention in interventions:
        for e in intervention.entities:

            # ---------- TANK (POINT) ----------
            if e.tank and e.tank.coordinates is not None:
                lon = db.query(func.ST_X(e.tank.coordinates)).scalar()
                lat = db.query(func.ST_Y(e.tank.coordinates)).scalar()

                results.append({
                    "type": "tank",
                    "id": e.tank.id_tank,
                    "coordinates": {"lat": lat, "lng": lon},
                    "intervention": intervention.id_interventions
                })

            # ---------- PIPE (LINESTRING GEOJSON) ----------
            if e.pipe and e.pipe.coordinates is not None:

                geojson_str = db.query(
                    func.ST_AsGeoJSON(e.pipe.coordinates)
                ).scalar()

                geojson = json.loads(geojson_str)

                results.append({
                    "type": "pipe",
                    "id": e.pipe.id_pipes,
                    "geometry": geojson,   # <-- AHORA ES JSON VALIDO
                    "intervention": intervention.id_interventions
                })

            # ---------- CONNECTION (POINT) ----------
            if e.connection and e.connection.coordinates is not None:

                lon = db.query(func.ST_X(e.connection.coordinates)).scalar()
                lat = db.query(func.ST_Y(e.connection.coordinates)).scalar()

                results.append({
                    "type": "connection",
                    "id": e.connection.id_connection,
                    "coordinates": {"lat": lat, "lng": lon},
                    "intervention": intervention.id_interventions
                })

    return results
