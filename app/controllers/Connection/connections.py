from fastapi import HTTPException, APIRouter, Depends
from app.models.connection.connections import Connection
from typing import List
from datetime import datetime 
from app.schemas.connections.connection import ConnectionResponse, ConnectionUpdate, ConnectionCreate
from app.db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.utils.response import success_response, error_response, existence_response_dict
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin
from app.models.pipes.pipes import Pipes
from app.utils.logger import create_log

def get_all(db: Session, page: int = 1, limit: int = 5):
    offset = (page - 1) * limit
    results = db.query(Connection).offset(offset).limit(limit).all()
    return results


def get_by_id(db: Session, id_connection: int):
    connection = db.query(Connection).filter(Connection.id_connection == id_connection).first()
    if not connection:
        raise HTTPException(status_code=404, detail="La conexión no existe")
    return connection


def create(db: Session, data,current_user: UserLogin):
    try:
        new_connection = Connection(
            coordenates=f'SRID=4326;POINT({data.longitude} {data.latitude})',
            material=data.material,
            diameter_mn=data.diameter_mn,
            pressure_nominal=data.pressure_nominal,
            connection_type=data.connection_type,
            depth_m=data.depth_m,
            installed_date=data.installed_date,
            installed_by=current_user.user,
            description=data.description,
            state=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Asociar tuberías si se especifican
        if data.pipe_ids:
            pipes = db.query(Pipes).filter(Pipes.id_pipes.in_(data.pipe_ids)).all()
            if len(pipes) != len(data.pipe_ids):
                raise HTTPException(status_code=404, detail="Una o más tuberías no existen.")
            new_connection.pipes = pipes

        db.add(new_connection)
        db.commit()
        db.refresh(new_connection)
        create_log(
            db,
            user_id=current_user.id_user,
            action = "CREATE",
            entity = "Connection",
            entity_id=new_connection.id_connection,
            description=f"El usuario {current_user.user} creó la conexión {new_connection.id_connection}"
        ) 
        return new_connection
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la conexión: {e}")


def update(db: Session, id_connection: int, data,current_user: UserLogin):
    connection = db.query(Connection).filter(Connection.id_connection == id_connection).first()
    if not connection:
        raise HTTPException(status_code=404, detail="La conexión no existe")

    try:
        if data.latitude and data.longitude:
            connection.coordenates = f"SRID=4326;POINT({data.longitude} {data.latitude})"
        elif data.latitude or data.longitude:
            raise HTTPException(status_code=400, detail="Ambas coordenadas deben proporcionarse juntas.")

        for field, value in data.dict(exclude_unset=True).items():
            if field not in ["latitude", "longitude", "pipe_ids"]:
                setattr(connection, field, value)

        if data.pipe_ids:
            pipes = db.query(Pipes).filter(Pipes.id_pipes.in_(data.pipe_ids)).all()
            if len(pipes) != len(data.pipe_ids):
                raise HTTPException(status_code=404, detail="Una o más tuberías no existen.")
            connection.pipes = pipes

        connection.updated_at = datetime.now()
        db.commit()
        db.refresh(connection)
        create_log(
            db,
            user_id=current_user.id_user,
            action = "UPDATE",
            entity = "Permission",
            entity_id=connection.id_connection,
            description=f"El usuario {current_user.user} actualizo la conexión {connection.id_connection}"
        ) 
        return connection
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar la conexión: {e}")


def toggle_state(db: Session, id_connection: int,current_user: UserLogin):
    connection = db.query(Connection).filter(Connection.id_connection == id_connection).first()
    if not connection:
        raise HTTPException(status_code=404, detail="La conexión no existe")

    connection.state = not connection.state
    connection.updated_at = datetime.now()
    db.commit()
    db.refresh(connection)
    
    status = ""
    if connection.state is False:
        status = "inactivo"
    else: 
        status = "activo" 
    create_log(
        db,
        user_id=current_user.id_user,
        action = "TOGGLE",
        entity = "Permission",
        entity_id=connection.id_connection,
        description=f"El usuario {current_user.user}, {status} la conexión {connection.id_connection}"
    ) 
    return connection