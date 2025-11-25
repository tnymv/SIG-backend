from fastapi import HTTPException, APIRouter, Depends
from app.models.connection.connections import Connection
from typing import List, Optional
from datetime import datetime 
from app.schemas.connections.connection import ConnectionResponse, ConnectionUpdate, ConnectionCreate,ConnectionBase
from app.db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.utils.response import success_response, error_response, existence_response_dict
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin
from app.models.pipes.pipes import Pipes
from app.utils.logger import create_log

def get_all(db: Session, page: int = 1, limit: int = 10000, search: Optional[str] = None, status: Optional[str] = None):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")

    offset = (page - 1) * limit
    
    query = db.query(
        Connection,
        func.ST_X(Connection.coordenates).label('longitude'),
        func.ST_Y(Connection.coordenates).label('latitude')
    )
    
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        search_filters = [
            func.lower(func.coalesce(Connection.material, '')).like(search_term),
            func.lower(func.coalesce(Connection.connection_type, '')).like(search_term),
            func.lower(func.coalesce(Connection.pressure_nominal, '')).like(search_term),
            func.lower(func.coalesce(Connection.installed_by, '')).like(search_term),
            func.lower(func.coalesce(Connection.description, '')).like(search_term)
        ]
        
        try:
            search_id = int(search.strip())
            search_filters.append(Connection.id_connection == search_id)
        except ValueError:
            pass
        
        query = query.filter(or_(*search_filters))
    
    # Filtrar por status si se proporciona
    if status:
        query = query.filter(Connection.status == status)

    count_query = db.query(Connection)
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        search_filters = [
            func.lower(func.coalesce(Connection.material, '')).like(search_term),
            func.lower(func.coalesce(Connection.connection_type, '')).like(search_term),
            func.lower(func.coalesce(Connection.pressure_nominal, '')).like(search_term),
            func.lower(func.coalesce(Connection.installed_by, '')).like(search_term),
            func.lower(func.coalesce(Connection.description, '')).like(search_term)
        ]
        
        try:
            search_id = int(search.strip())
            search_filters.append(Connection.id_connection == search_id)
        except ValueError:
            pass
        
        count_query = count_query.filter(or_(*search_filters))
    
    # Aplicar filtro de status también al count_query
    if status:
        count_query = count_query.filter(Connection.status == status)
    
    total = count_query.count()
    
    connections = query.order_by(Connection.id_connection.desc()).offset(offset).limit(limit).all()

    if not connections and not search:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "No se encontraron conexiones")
        )

    connection_response = []

    for conn, longitude, latitude in connections:
        conn_data = {
            "id_connection": conn.id_connection,
            "latitude": latitude,
            "longitude": longitude,
            "material": conn.material,
            "diameter_mn": conn.diameter_mn,
            "pressure_nominal": conn.pressure_nominal,
            "connection_type": conn.connection_type,
            "depth_m": conn.depth_m,
            "installed_date": conn.installed_date,
            "installed_by": conn.installed_by,
            "description": conn.description,
            "status": conn.status,
            "active": conn.active,
            "created_at": conn.created_at,
            "updated_at": conn.updated_at,
            "pipes": [
                {
                    "id_pipes": pipe.id_pipes,
                    "material": pipe.material,
                    "diameter": pipe.diameter
                }
                for pipe in conn.pipes
            ],
        }
        connection_response.append(conn_data)
    
    return connection_response, total


def get_by_id(db: Session, id_connection: int):
    result = db.query(
        Connection,
        func.ST_X(Connection.coordenates).label('longitude'),
        func.ST_Y(Connection.coordenates).label('latitude')
    ).filter(Connection.id_connection == id_connection).first()

    if not result:
        raise HTTPException(status_code=404, detail="La conexión no existe")

    conn, longitude, latitude = result

    conn_data = {
        "id_connection": conn.id_connection,
        "latitude": latitude,
        "longitude": longitude,
        "material": conn.material,
        "diameter_mn": conn.diameter_mn,
        "pressure_nominal": conn.pressure_nominal,
        "connection_type": conn.connection_type,
        "depth_m": conn.depth_m,
        "installed_date": conn.installed_date,
        "installed_by": conn.installed_by,
        "description": conn.description,
        "status": conn.status,
        "active": conn.active,
        "created_at": conn.created_at,
        "updated_at": conn.updated_at,
        "pipes": [
            {"id_pipes": p.id_pipes, "material": p.material, "diameter": p.diameter}
            for p in conn.pipes
        ]
    }

    return conn_data


def create(db: Session, data: ConnectionBase,current_user: UserLogin):
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
            status=data.status.value if hasattr(data.status, 'value') else data.status,
            active=True,
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
        response = ConnectionResponse(
            id_connection=new_connection.id_connection,
            latitude=data.latitude,
            longitude=data.longitude,
            material=new_connection.material,
            diameter_mn=new_connection.diameter_mn,
            pressure_nominal=new_connection.pressure_nominal,
            connection_type=new_connection.connection_type,
            depth_m=new_connection.depth_m,
            installed_date=new_connection.installed_date,
            installed_by=new_connection.installed_by,
            description=new_connection.description,
            status=new_connection.status,
            active=new_connection.active,
            created_at=new_connection.created_at,
            updated_at=new_connection.updated_at,
            pipes=[{"id_pipes": pipe.id_pipes, "material": pipe.material, "diameter": pipe.diameter} for pipe in new_connection.pipes]
        )
        
        return response
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la conexión: {e}")


def update(db: Session, id_connection: int, data, current_user: UserLogin):
    connection = db.query(Connection).filter(Connection.id_connection == id_connection).first()
    if not connection:
        raise HTTPException(status_code=404, detail="La conexión no existe")

    try:
        if data.latitude is not None and data.longitude is not None:
            connection.coordenates = f'SRID=4326;POINT({data.longitude} {data.latitude})'
        elif data.latitude is not None or data.longitude is not None:
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
            action="UPDATE",
            entity="Connection",
            entity_id=connection.id_connection,
            description=f"El usuario {current_user.user} actualizó la conexión {connection.id_connection}"
        )

        longitude = db.scalar(func.ST_X(connection.coordenates))
        latitude = db.scalar(func.ST_Y(connection.coordenates))

        response = {
            "id_connection": connection.id_connection,
            "latitude": latitude,
            "longitude": longitude,
            "material": connection.material,
            "diameter_mn": connection.diameter_mn,
            "pressure_nominal": connection.pressure_nominal,
            "connection_type": connection.connection_type,
            "depth_m": connection.depth_m,
            "installed_date": connection.installed_date,
            "installed_by": connection.installed_by,
            "description": connection.description,
            "status": connection.status,
            "active": connection.active,
            "created_at": connection.created_at,
            "updated_at": connection.updated_at,
            "pipes": [
                {"id_pipes": p.id_pipes, "material": p.material, "diameter": p.diameter}
                for p in connection.pipes
            ]
        }

        return response

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar la conexión: {e}")



def toggle_state(db: Session, id_connection: int,current_user: UserLogin):
    connection = db.query(Connection).filter(Connection.id_connection == id_connection).first()
    if not connection:
        raise HTTPException(status_code=404, detail="La conexión no existe")

    connection.active = not connection.active
    connection.updated_at = datetime.now()
    db.commit()
    db.refresh(connection)
    
    status = ""
    if connection.active is False:
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