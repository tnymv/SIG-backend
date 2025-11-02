from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.user.user import UserLogin
from app.schemas.files.files import FilesResponse, FilesCreate, FilesUpdate
from app.controllers.files.files import (
    get_all, get_by_id, create, update, toggle_state
)
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/files", tags=["Files"])

# 🔹 Obtener todos los archivos
@router.get("", response_model=List[FilesResponse])
async def list_files(
    page: int = 1,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        files = get_all(db, page, limit)
        return success_response([
            FilesResponse.model_validate(f).model_dump(mode="json") for f in files
        ])
    except Exception as e:
        return error_response(f"Error al obtener los archivos: {e}")


# 🔹 Obtener archivo por ID
@router.get("/{file_id}", response_model=FilesResponse)
async def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        file = get_by_id(db, file_id)
        return success_response(FilesResponse.model_validate(file).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener el archivo: {e}")


# 🔹 Crear archivo
@router.post("", response_model=FilesResponse)
async def create_file(
    data: FilesCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        new_file = create(db, data, current_user)
        return success_response(FilesResponse.model_validate(new_file).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear el archivo: {e}")


# 🔹 Actualizar archivo
@router.put("/{file_id}", response_model=FilesResponse)
async def update_file(
    file_id: int,
    data: FilesUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        updated_file = update(db, file_id, data, current_user)
        return success_response(FilesResponse.model_validate(updated_file).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar el archivo: {e}")


# 🔹 Activar/desactivar archivo
@router.delete("/{file_id}")
async def toggle_file_state(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        file = toggle_state(db, file_id, current_user)
        action = "activó" if file.status else "desactivó"
        return success_response({
            "message": f"El usuario {current_user.user} {action} el archivo {file.taxpayer} {file.cologne} correctamente."
        })
    except Exception as e:
        return error_response(f"Error al cambiar el estado del archivo: {e}")
