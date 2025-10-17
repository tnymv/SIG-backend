from fastapi import HTTPException, APIRouter, Depends
from app.models.connection.connections import Connection
from typing import List
from datetime import datetime 
from app.schemas.connections.connection import ConnectionBase, ConnectionResponse, ConnectionUpdate, ConnectionCreate
from app.db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.utils.response import success_response, error_response, existence_response_dict
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin
from app.utils.logger import create_log

router = APIRouter(prefix="/connections", tags=['Connections'])

@router.get('', response_model = List[ConnectionResponse])
async def get_all_connections(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 5,
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        if page < 1 or limit < 1:
            raise HTTPException(
                status_code=400,
                detail=" La página y el mímite deben ser mayores a 0"
            )
        offset = (page - 1) * limit
        connection = db.query(
            Connection,
            func.ST_X(Connection.coordenates).label('longitude'),
            func.ST_Y(Connection.coordenates).label('latitude')
        ).offset(offset).limit(limit).all()
        
        if not connection: 
            return success_response(data=[], message="No hay conexiones registradas")
        
        connection_response = []
        for conn, longitude, latitude in connection:
            conn_data = {
                "id_connection": conn.id_connection,
                "id_pipe": conn.id_pipe,
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
            }
            connection_response.append(ConnectionResponse(**conn_data).model_dump(mode="json"))
        
        return success_response(
            data=connection_response,
            message="Conexiones obtenidas correctamente"
        )
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
            raise HTTPException(
                status_code=404,
                detail=existence_response_dict(False, "La conexión no existe"),
                headers={"X-Error": "La conexión no existe"}
            )
        conn, longitude, latitude = result
        
        conn_data = {
            "id_connection": conn.id_connection,
            "id_pipe": conn.id_pipe,
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
        }
        return success_response(ConnectionResponse(**conn_data).model_dump(mode="json"), "Conexión obtenida correctamente")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener la conexión: {str(e)}",
            headers={"X-Error": f"Error al obtener la conexión: {str(e)}"}
        )

@router.post('', response_model = ConnectionBase)
async def create_connection(
    connection_data: ConnectionCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    if db.query(Connection).filter(Connection.id_pipe == connection_data.id_pipe).first():
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "La conexión ya existe"),
            headers={"X-Error": "La conexión ya existe"}
        )
    try: 
        new_connection = Connection(
            id_pipe=connection_data.id_pipe,
            coordenates=f'POINT({connection_data.longitude} {connection_data.latitude})',
            material=connection_data.material,
            diameter_mn=connection_data.diameter_mn,
            pressure_nominal=connection_data.pressure_nominal,
            connection_type=connection_data.connection_type,
            depth_m=connection_data.depth_m,
            installed_date=connection_data.installed_date,
            installed_by=current_user.user,
            description=connection_data.description,
            state= True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(new_connection)
        db.commit()
        db.refresh(new_connection)
        connection_reponse = ConnectionResponse(
            id_connection=new_connection.id_connection,
            id_pipe=new_connection.id_pipe,
            latitude=connection_data.latitude,
            longitude=connection_data.longitude,
            material=new_connection.material,
            diameter_mn=new_connection.diameter_mn,
            pressure_nominal=new_connection.pressure_nominal,
            connection_type=new_connection.connection_type,
            depth_m=new_connection.depth_m,
            installed_date=new_connection.installed_date,
            installed_by=current_user.user,
            description=new_connection.description,
            state=new_connection.state,
            created_at=new_connection.created_at,
            updated_at=new_connection.updated_at
        )
        
        return success_response(connection_reponse.model_dump(mode="json"), "Conexión creada correctamente")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la conexión: {str(e)}")
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear la conexión: {str(e)}",
            headers={"X-Error": f"Error al crear la conexión: {str(e)}"}
        )

@router.put('/{connection_id}', response_model=ConnectionResponse)
async def update_connection(
    connection_id: int,
    connection_data: ConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    connection = db.query(Connection).filter(Connection.id_connection == connection_id).first()
    if not connection:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "La conexión no existe"),
            headers={"X-Error": "La conexión no existe"}
        )
    
    if connection_data.id_pipe != connection.id_pipe:
        if db.query(Connection).filter(Connection.id_pipe == connection_data.id_pipe).first():
            raise HTTPException(
                status_code=409,
                detail=existence_response_dict(True, "La conexión con el id_pipe proporcionado ya existe"),
                headers={"X-Error": "La conexión con el id_pipe proporcionado ya existe"}
            )
    try:
        if connection_data.id_pipe is not None:
            connection.id_pipe = connection_data.id_pipe
        
        if connection_data.latitude is not None and connection_data.longitude is not None:
            connection.coordenates = f"SRID=4326;POINT({connection_data.longitude} {connection_data.latitude})"
        elif connection_data.latitude is not None or connection_data.longitude is not None:
            raise HTTPException(
                status_code=400,
                detail="Ambas coordenadas (latitud y longitud) deben ser proporcionadas juntas.",
                headers={"X-Error": "Coordenadas incompletas"}
            )
        if connection_data.material is not None:
            connection.material = connection_data.material
        if connection_data.diameter_mn is not None:
            connection.diameter_mn = connection_data.diameter_mn
        if connection_data.pressure_nominal is not None:
            connection.pressure_nominal = connection_data.pressure_nominal
        if connection_data.connection_type is not None:
            connection.connection_type = connection_data.connection_type
        if connection_data.depth_m is not None:
            connection.depth_m = connection_data.depth_m
        if connection_data.installed_date is not None:
            connection.installed_date = connection_data.installed_date
        if connection_data.installed_by is not None:
            connection.installed_by = connection_data.installed_by
        if connection_data.description is not None:
            connection.description = connection_data.description
        if connection_data.state is not None:
            connection.state = connection_data.state
        connection.updated_at = datetime.now()
        
        db.commit()
        db.refresh(connection)
        result = db.query(
            Connection,
            func.ST_X(Connection.coordenates).label('longitude'),
            func.ST_Y(Connection.coordenates).label('latitude')
        ).filter(Connection.id_connection == connection_id).first()
        
        conn, longitude, latitude = result
        conn_data = {
            "id_connection": conn.id_connection,
            "id_pipe": conn.id_pipe,
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
        }
        return success_response(ConnectionResponse(**conn_data).model_dump(mode="json"), "Conexión actualizada correctamente")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar la conexión: {str(e)}",
            headers={"X-Error": f"Error al actualizar la conexión: {str(e)}"}
        )
@router.delete('/{connection_id}', response_model=ConnectionResponse)
async def delete_connection(
    connection_id: int, 
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    connection = db.query(Connection).filter(Connection.id_connection == connection_id).first()
    if not connection: 
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "La conexión no existe"),
            headers={"X-Error": "La conexión no existe"}
        )
    
    try:
        connection.state = not connection.state
        connection.updated_at = datetime.now()
        db.commit()
        db.refresh(connection)
        action_description = "activó" if connection.state else "desactivó"
        
        status_message = "Tanque activado exitosamente" if connection.state else "Tanque desactivado exitosamente"
        return success_response(status_message, f"Conexión {action_description} correctamente")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar el estado de la conexión: {str(e)}",
            headers={"X-Error": f"Error al actualizar el estado de la conexión: {str(e)}"}
        )