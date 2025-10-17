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

router = APIRouter(prefix="/connections", tags=['Connections'])

@router.get('', response_model=List[ConnectionResponse])
async def get_all_connections(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 5,
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores a 0")
        
        offset = (page - 1) * limit
        connections = db.query(
            Connection,
            func.ST_X(Connection.coordenates).label('longitude'),
            func.ST_Y(Connection.coordenates).label('latitude')
        ).offset(offset).limit(limit).all()

        if not connections: 
            return success_response(data=[], message="No hay conexiones registradas")
        
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
                "state": conn.state,
                "created_at": conn.created_at,
                "updated_at": conn.updated_at,
                "pipes": [{"id_pipes": pipe.id_pipes, "material": pipe.material, "diameter": pipe.diameter} for pipe in conn.pipes]
            }
            connection_response.append(ConnectionResponse(**conn_data).model_dump(mode="json"))
        
        return success_response(data=connection_response, message="Conexiones obtenidas correctamente")
    except Exception as e:
        return error_response(f"Error al obtener las conexiones: {str(e)}")

@router.get('/{connection_id}', response_model=ConnectionResponse)
async def get_connection_by_id(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        result = db.query(
            Connection,
            func.ST_X(Connection.coordenates).label('longitude'),
            func.ST_Y(Connection.coordenates).label('latitude')
        ).filter(Connection.id_connection == connection_id).first()

        if not result: 
            raise HTTPException(status_code=404, detail=existence_response_dict(False, "La conexión no existe"))

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
            "installed_by": current_user.user,
            "description": conn.description,
            "state": conn.state,
            "created_at": conn.created_at,
            "updated_at": conn.updated_at,
            "pipes": [{"id_pipes": pipe.id_pipes, "material": pipe.material, "diameter": pipe.diameter} for pipe in conn.pipes]
        }
        return success_response(ConnectionResponse(**conn_data).model_dump(mode="json"), "Conexión obtenida correctamente")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la conexión: {str(e)}")

@router.post('', response_model=ConnectionResponse)
async def create_connection(
    connection_data: ConnectionCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        # Crear conexión base
        new_connection = Connection(
            coordenates=f'SRID=4326;POINT({connection_data.longitude} {connection_data.latitude})',
            material=connection_data.material,
            diameter_mn=connection_data.diameter_mn,
            pressure_nominal=connection_data.pressure_nominal,
            connection_type=connection_data.connection_type,
            depth_m=connection_data.depth_m,
            installed_date=connection_data.installed_date,
            installed_by=current_user.user,
            description=connection_data.description,
            state=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 🔹 Asociar pipes si existen
        if connection_data.pipe_ids:
            pipes = db.query(Pipes).filter(Pipes.id_pipes.in_(connection_data.pipe_ids)).all()
            if len(pipes) != len(connection_data.pipe_ids):
                raise HTTPException(status_code=404, detail="Una o más tuberías no existen.")
            new_connection.pipes = pipes

        db.add(new_connection)
        db.commit()
        db.refresh(new_connection)

        response = ConnectionResponse(
            id_connection=new_connection.id_connection,
            latitude=connection_data.latitude,
            longitude=connection_data.longitude,
            material=new_connection.material,
            diameter_mn=new_connection.diameter_mn,
            pressure_nominal=new_connection.pressure_nominal,
            connection_type=new_connection.connection_type,
            depth_m=new_connection.depth_m,
            installed_date=new_connection.installed_date,
            installed_by=new_connection.installed_by,
            description=new_connection.description,
            state=new_connection.state,
            created_at=new_connection.created_at,
            updated_at=new_connection.updated_at,
            pipes=[{"id_pipes": pipe.id_pipes, "material": pipe.material, "diameter": pipe.diameter} for pipe in new_connection.pipes]
        )
        return success_response(response.model_dump(mode="json"), "Conexión creada correctamente")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la conexión: {str(e)}")

@router.put('/{connection_id}', response_model=ConnectionResponse)
async def update_connection(
    connection_id: int,
    connection_data: ConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    connection = db.query(Connection).filter(Connection.id_connection == connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "La conexión no existe"))

    try:
        if connection_data.latitude is not None and connection_data.longitude is not None:
            connection.coordenates = f"SRID=4326;POINT({connection_data.longitude} {connection_data.latitude})"
        elif connection_data.latitude is not None or connection_data.longitude is not None:
            raise HTTPException(status_code=400, detail="Ambas coordenadas deben ser proporcionadas juntas.")

        for field, value in connection_data.dict(exclude_unset=True).items():
            if field not in ["latitude", "longitude", "pipe_ids"]:
                setattr(connection, field, value)

        if connection_data.pipe_ids is not None:
            pipes = db.query(Pipes).filter(Pipes.id_pipes.in_(connection_data.pipe_ids)).all()
            if len(pipes) != len(connection_data.pipe_ids):
                raise HTTPException(status_code=404, detail="Una o más tuberías no existen.")
            connection.pipes = pipes

        connection.updated_at = datetime.now()
        db.commit()
        db.refresh(connection)

        lat = db.scalar(func.ST_Y(connection.coordenates))
        lon = db.scalar(func.ST_X(connection.coordenates))

        pipes_data = [
            {
                "id_pipes": p.id_pipes,
                "material": getattr(p, "material", None),
                "diameter": float(getattr(p, "diameter", 0)) if getattr(p, "diameter", None) is not None else None
            }
            for p in connection.pipes
        ]

        response_data = ConnectionResponse(
            id_connection=connection.id_connection,
            latitude=lat,
            longitude=lon,
            material=connection.material,
            diameter_mn=float(connection.diameter_mn) if connection.diameter_mn else None,
            pressure_nominal=connection.pressure_nominal,
            connection_type=connection.connection_type,
            depth_m=float(connection.depth_m) if connection.depth_m else None,
            installed_date=connection.installed_date,
            installed_by=connection.installed_by,
            description=connection.description,
            state=connection.state,
            created_at=connection.created_at,
            updated_at=connection.updated_at,
            pipes=pipes_data
        )

        return success_response(response_data.model_dump(mode="json"), "Conexión creada correctamente")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar la conexión: {str(e)}")



@router.delete('/{connection_id}')
async def delete_connection(
    connection_id: int, 
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    connection = db.query(Connection).filter(Connection.id_connection == connection_id).first()
    if not connection: 
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "La conexión no existe"))
    
    try:
        connection.state = not connection.state
        connection.updated_at = datetime.now()
        db.commit()
        db.refresh(connection)
        action = "activó" if connection.state else "desactivó"
        msg = f"Conexión {action} correctamente"
        return success_response(msg, msg)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar el estado: {str(e)}")