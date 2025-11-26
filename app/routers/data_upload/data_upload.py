from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.user.user import UserLogin
from app.schemas.data_upload.data_upload import Data_uploadResponse, Data_uploadCreate, Data_uploadUpdate
from app.controllers.data_upload.data_upload import (
    get_all, get_by_identifier,  update, toggle_state,  process_excel_data
)
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/data-upload", tags=["Data Upload"])

@router.get('', response_model=List[Data_uploadResponse])
async def list_data_uploads(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=10000, description="Límite de resultados por página"),
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        data_uploads, total = get_all(db, page, limit)
        total_pages = (total + limit - 1) // limit
        next_page = page + 1 if page < total_pages else None
        prev_page = page - 1 if page > 1 else None

        data = [Data_uploadResponse.model_validate(du).model_dump(mode="json") for du in data_uploads]

        return success_response({
            "items": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total,
                "total_pages": total_pages,
                "next_page": next_page,
                "prev_page": prev_page
            }
        })
    except Exception as e:
        # Detectar errores de base de datos (tabla no existe)
        error_str = str(e).lower()
        if 'does not exist' in error_str or 'undefinedtable' in error_str or 'relation' in error_str:
            # Si la tabla no existe, devolver respuesta vacía en lugar de error
            return success_response({
                "items": [],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_items": 0,
                    "total_pages": 0,
                    "next_page": None,
                    "prev_page": None
                }
            }, "No hay registros disponibles")
        # Para otros errores, devolver mensaje genérico sin detalles técnicos
        return error_response("No se pudieron cargar los registros. Por favor, intenta nuevamente.")

@router.get("/{identifier}", response_model=Data_uploadResponse)
async def get_data_upload(
    identifier: str,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        data_upload = get_by_identifier(db, identifier)
        return success_response(Data_uploadResponse.model_validate(data_upload).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener el registro de data upload: {e}")


# ✅ NUEVO ENDPOINT PARA SUBIR EXCEL
@router.post("/upload-excel")
async def upload_excel_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):

    try:
        # Verificar tipo de archivo
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return error_response("Solo se permiten archivos Excel (.xlsx, .xls)")
        
        # Leer archivo
        contents = await file.read()
        if len(contents) == 0:
            return error_response("El archivo está vacío")
        
        # Procesar Excel
        result = process_excel_data(db, contents, current_user)
        
        if result["success"]:
            message = result.get("message") or f"Archivo '{file.filename}' procesado exitosamente"
            return success_response({
                "message": message,
                "created_records": result.get("created_records", 0),
                "total_processed": result.get("total_processed", 0),
                "errors": result.get("errors", []),
                "filename": file.filename
            })
        else:
            error_message = result.get("message") or "Error al procesar archivo"
            return error_response({
                "message": error_message,
                "errors": result.get("errors", []),
                "filename": file.filename
            })
            
    except Exception as e:
        return error_response(f"Error al subir archivo: {str(e)}")

@router.put("/{identifier}", response_model=Data_uploadResponse)
async def update_data_upload(
    identifier: str,
    data: Data_uploadUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        updated_data_upload = update(db, identifier, data, current_user)
        return success_response(Data_uploadResponse.model_validate(updated_data_upload).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar el registro de data upload: {e}")

@router.delete("/{identifier}")
async def toggle_data_upload_state(
    identifier: str,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        data_upload = toggle_state(db, identifier, current_user)
        action = "activó" if data_upload.status else "desactivó"
        return success_response({
            "message": f"El usuario {current_user.user} {action} el registro {data_upload.taxpayer} - {data_upload.cologne} correctamente."
        })
    except Exception as e:
        return error_response(f"Error al cambiar el estado del registro de data upload: {e}")