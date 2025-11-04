from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin
from app.schemas.connections.connection import ConnectionCreate, ConnectionUpdate, ConnectionResponse
from app.controllers.Connection.connections import get_all, get_by_id, create, update, toggle_state
from app.utils.response import success_response, error_response
from typing import List

router = APIRouter(prefix="/connections", tags=["Connections"])

@router.get('', response_model=List[ConnectionResponse])
async def list_connections(
    page: int = 1,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        connections = get_all(db, page, limit)
        return success_response([ConnectionResponse.model_validate(conn).model_dump(mode="json") for conn in connections])
    except Exception as e:
        return error_response(f"Error al obtener las conexiones: {e}")

@router.get('/{connection_id}', response_model=ConnectionResponse)
async def get_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        connection = get_by_id(db, connection_id)
        return success_response(ConnectionResponse.model_validate(connection).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener la conexión: {e}")

@router.post('', response_model=ConnectionResponse)
async def create_connection(
    data: ConnectionCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        new_connection = create(db, data, current_user.user,current_user)
        return success_response(ConnectionResponse.model_validate(new_connection).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear la conexión: {e}")

@router.put('/{connection_id}', response_model=ConnectionResponse)
async def update_connection(
    connection_id: int,
    data: ConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        updated_connection = update(db, connection_id, data,current_user)
        return success_response(ConnectionResponse.model_validate(updated_connection).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar la conexión: {e}")

@router.delete('/{connection_id}')
async def toggle_connection_state(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        toggle_connection = toggle_state(db, connection_id,current_user)
        action = "activó" if toggle_connection.state else "desactivó"
        return success_response({
            "message": f"Se {action} la conexión correctamente."
        })
    except Exception as e:
        return error_response(f"Error al cambiar el estado de la conexión: {e}")