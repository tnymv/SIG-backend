from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.user.user import UserLogin
from app.schemas.data_upload.data_upload import Data_uploadResponse, Data_uploadCreate, Data_uploadUpdate
from app.controllers.data_upload.data_upload import (
    get_all, get_by_id, create, update, toggle_state, create_bulk, process_excel_data
)
from app.controllers.auth.auth_controller import get_current_active_user
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/data-upload", tags=["Data Upload"])

@router.get('', response_model=List[Data_uploadResponse])
async def list_data_uploads(
    page: int = 1,
    limit: int = 10,
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
        return error_response(f"Error al obtener los registros de data upload: {e}")

@router.get("/{data_upload_id}", response_model=Data_uploadResponse)
async def get_data_upload(
    data_upload_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        data_upload = get_by_id(db, data_upload_id)
        return success_response(Data_uploadResponse.model_validate(data_upload).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al obtener el registro de data upload: {e}")

@router.post("", response_model=Data_uploadResponse)
async def create_data_upload(
    data: Data_uploadCreate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        new_data_upload = create(db, data, current_user)
        return success_response(Data_uploadResponse.model_validate(new_data_upload).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al crear el registro de data upload: {e}")

@router.post("/bulk", response_model=List[Data_uploadResponse])
async def create_bulk_data_uploads(
    data_list: List[Data_uploadCreate],
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        created_records = create_bulk(db, data_list, current_user)
        data = [Data_uploadResponse.model_validate(du).model_dump(mode="json") for du in created_records]
        return success_response({
            "message": f"Se crearon {len(created_records)} registros exitosamente",
            "items": data
        })
    except Exception as e:
        return error_response(f"Error al crear los registros de data upload: {e}")

# ✅ NUEVO ENDPOINT PARA SUBIR EXCEL
@router.post("/upload-excel")
async def upload_excel_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    """
    Sube y procesa un archivo Excel con datos de servicios
    
    - **file**: Archivo Excel (.xlsx, .xls) con la estructura SIAF
    - **Returns**: Resultado del procesamiento con conteo de registros creados
    """
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
            return success_response({
                "message": f"✅ Archivo '{file.filename}' procesado exitosamente",
                "created_records": result["created_records"],
                "total_processed": result["total_processed"],
                "errors": result["errors"],
                "filename": file.filename
            })
        else:
            return error_response({
                "message": "❌ Error al procesar archivo",
                "errors": result["errors"],
                "filename": file.filename
            })
            
    except Exception as e:
        return error_response(f"Error al subir archivo: {str(e)}")

@router.put("/{data_upload_id}", response_model=Data_uploadResponse)
async def update_data_upload(
    data_upload_id: int,
    data: Data_uploadUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        updated_data_upload = update(db, data_upload_id, data, current_user)
        return success_response(Data_uploadResponse.model_validate(updated_data_upload).model_dump(mode="json"))
    except Exception as e:
        return error_response(f"Error al actualizar el registro de data upload: {e}")

@router.delete("/{data_upload_id}")
async def toggle_data_upload_state(
    data_upload_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        data_upload = toggle_state(db, data_upload_id, current_user)
        action = "activó" if data_upload.status else "desactivó"
        return success_response({
            "message": f"El usuario {current_user.user} {action} el registro {data_upload.taxpayer} - {data_upload.cologne} correctamente."
        })
    except Exception as e:
        return error_response(f"Error al cambiar el estado del registro de data upload: {e}")