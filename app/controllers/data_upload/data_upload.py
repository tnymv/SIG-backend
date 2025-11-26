from fastapi import HTTPException
from app.models.data_upload.data_upload import Data_upload
from typing import List
from datetime import datetime
from app.schemas.data_upload.data_upload import Data_uploadBase, Data_uploadCreate, Data_uploadResponse, Data_uploadUpdate
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.logger import create_log
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin
import pandas as pd
import io
import sys
import os

# la ruta de scripts al path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

# importar el script
from app.scripts.data_upload.data_upload import process_excel_from_content

def get_all(db: Session, page: int, limit: int):
    offset = (page - 1) * limit
    
    data_uploads = db.query(Data_upload).offset(offset).limit(limit).all()
    query = db.query(Data_upload)
    total = query.count()
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Página y límite deben ser mayores que 0")
    return data_uploads, total

def get_by_identifier(db: Session, identifier: int):
    data_upload = db.query(Data_upload).filter(Data_upload.identifier == identifier).first()
    if not data_upload:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "El registro de data upload no existe"))
    return data_upload


def create_bulk(db: Session, data_list: List[Data_uploadCreate], current_user: UserLogin):
    """Crea múltiples registros a la vez"""
    created_records = []
    
    for data in data_list:
        # Verificar si ya existe
        existing = db.query(Data_upload).filter(
            Data_upload.taxpayer == data.taxpayer, 
            Data_upload.cologne == data.cologne
        ).first()
        
        if existing:
            continue  # Saltar si ya existe
        
        new_data_upload = Data_upload(
            # Encabezado
            siaf=data.siaf,
            institutional_classification=data.institutional_classification,
            report=data.report,
            date=data.date,
            hour=data.hour,
            seriereport=data.seriereport,
            user=data.user,
            # Información del servicio
            identifier=data.identifier,
            taxpayer=data.taxpayer,
            cologne=data.cologne,
            cat_service=data.cat_service,
            cannon=data.cannon,
            excess=data.excess,
            total=data.total,
            status=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(new_data_upload)
        created_records.append(new_data_upload)
    
    db.commit()
    
    # Refresh todos los registros creados
    for record in created_records:
        db.refresh(record)
    
    create_log(
        db,
        user_id=current_user.id_user,
        action="CREATE",
        entity="Data_upload",
        entity_id=None,
        description=f"El usuario {current_user.user} creó {len(created_records)} registros de data upload"
    )

    return created_records

def update(db: Session, identifier: int, data: Data_uploadUpdate, current_user: UserLogin):
    data_upload = db.query(Data_upload).filter(Data_upload.identifier == identifier).first()
    if not data_upload:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, f"El registro con identifier '{identifier}' no existe"))

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(data_upload, field, value)

    data_upload.updated_at = datetime.now()
    db.commit()
    db.refresh(data_upload)

    create_log(
        db,
        user_id=current_user.id_user,
        action="UPDATE",
        entity="Data_upload",
        entity_id=None,
        description=f"El usuario {current_user.user} actualizó el registro {data_upload.taxpayer} - {data_upload.cologne} (Identifier: {data_upload.identifier})"
    )


    return data_upload

def toggle_state(db: Session, identifier: int, current_user: UserLogin):
    data_upload = db.query(Data_upload).filter(Data_upload.identifier == identifier).first()
    if not data_upload:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "El registro '{identifier}' no existe"))

    data_upload.status = not data_upload.status
    data_upload.updated_at = datetime.now()
    db.commit()
    db.refresh(data_upload)

    create_log(
        db,
        user_id=current_user.id_user,
        action="UPDATE",
        entity="Data_upload",
        entity_id=None,
        description=f"El usuario {current_user.user} {'activó' if data_upload.status else 'desactivó'} el registro {data_upload.taxpayer} - {data_upload.cologne} (Identifier: {data_upload.identifier})"
    )

    return data_upload

# FUncion para procesar el excel usando el script
def process_excel_data(db: Session, file_content: bytes, current_user: UserLogin):
    try:
        print(" Ejecutando script de procesamiento Excel...")
        
        # Convertir a BytesIO (necesario para pandas)
        file_io = io.BytesIO(file_content)
        
        # Llamar el script
        processed_data, errors = process_excel_from_content(file_io, current_user)
        
        print(f"Script retornó: {len(processed_data)} datos válidos, {len(errors)} errores")
        
        # Insertar en BD
        if processed_data:
            created_records = create_bulk(db, processed_data, current_user)
            return {
                "success": True,
                "created_records": len(created_records),
                "total_processed": len(processed_data),
                "errors": errors
            }
        else:
            return {
                "success": False,
                "errors": errors,
                "message": "No se pudieron procesar registros"
            }
            
    except Exception as e:
        error_msg = f"Error al ejecutar script: {str(e)}"
        print(f" {error_msg}")
        return {
            "success": False,
            "errors": [error_msg]
        }