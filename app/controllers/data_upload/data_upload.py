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
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Página y límite deben ser mayores que 0")
    
    try:
        offset = (page - 1) * limit
        data_uploads = db.query(Data_upload).offset(offset).limit(limit).all()
        query = db.query(Data_upload)
        total = query.count()
        return data_uploads, total
    except Exception as e:
        # Si la tabla no existe, devolver lista vacía en lugar de error
        error_str = str(e).lower()
        if 'does not exist' in error_str or 'undefinedtable' in error_str or 'relation' in error_str:
            return [], 0
        # Para otros errores, relanzar
        raise

def get_by_identifier(db: Session, identifier: str):
    data_upload = db.query(Data_upload).filter(Data_upload.identifier == identifier).first()
    if not data_upload:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "El registro de data upload no existe"))
    return data_upload


def create_bulk(db: Session, data_list: List[Data_uploadCreate], current_user: UserLogin):
    """Crea múltiples registros a la vez o actualiza si ya existen"""
    created_records = []
    updated_records = []
    
    for data in data_list:
        # Verificar si ya existe por identifier (clave primaria)
        existing = db.query(Data_upload).filter(
            Data_upload.identifier == data.identifier
        ).first()
        
        if existing:
            # Actualizar registro existente
            existing.siaf = data.siaf
            existing.municipality = data.municipality
            existing.department = data.department
            existing.institutional_classification = data.institutional_classification
            existing.report = data.report
            existing.date = data.date
            existing.hour = data.hour
            existing.seriereport = data.seriereport
            existing.user = data.user
            existing.taxpayer = data.taxpayer
            existing.cologne = data.cologne
            existing.cat_service = data.cat_service
            existing.cannon = data.cannon
            existing.excess = data.excess
            existing.total = data.total
            existing.updated_at = datetime.now()
            # Marcar como actualizado agregando un atributo temporal
            setattr(existing, '_was_updated', True)
            updated_records.append(existing)
            continue
        
        # Crear nuevo registro
        new_data_upload = Data_upload(
            # Encabezado
            siaf=data.siaf,
            municipality=data.municipality,
            department=data.department,
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
        setattr(new_data_upload, '_was_updated', False)
        created_records.append(new_data_upload)
    
    db.commit()
    
    # Refresh todos los registros creados y actualizados
    for record in created_records:
        db.refresh(record)
    for record in updated_records:
        db.refresh(record)
    
    # Log solo si hay registros creados o actualizados
    if created_records or updated_records:
        action_desc = []
        if created_records:
            action_desc.append(f"creó {len(created_records)} registros")
        if updated_records:
            action_desc.append(f"actualizó {len(updated_records)} registros")
        
        create_log(
            db,
            user_id=current_user.id_user,
            action="CREATE" if created_records else "UPDATE",
            entity="Data_upload",
            entity_id=None,
            description=f"El usuario {current_user.user} {', '.join(action_desc)} de data upload"
        )

    # Retornar todos los registros con información de si fueron creados o actualizados
    all_records = created_records + updated_records
    return all_records

def update(db: Session, identifier: str, data: Data_uploadUpdate, current_user: UserLogin):
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

def toggle_state(db: Session, identifier: str, current_user: UserLogin):
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

# Función para procesar el excel usando el script
def process_excel_data(db: Session, file_content: bytes, current_user: UserLogin):
    try:
        print(" Ejecutando script de procesamiento Excel...")
        
        # Convertir a BytesIO (necesario para pandas)
        file_io = io.BytesIO(file_content)
        
        # Llamar el script
        processed_data, errors = process_excel_from_content(file_io, current_user)
        
        print(f"Script retornó: {len(processed_data)} datos válidos, {len(errors)} errores")
        
        # Si hay errores críticos (formato incorrecto, columnas faltantes), devolver error
        if errors and len(processed_data) == 0:
            # Verificar si son errores críticos de formato
            critical_errors = [e for e in errors if any(keyword in e.lower() for keyword in [
                'columna', 'columnas', 'formato', 'vacío', 'válido', 'requerida'
            ])]
            if critical_errors:
                return {
                    "success": False,
                    "errors": errors,
                    "message": "El archivo Excel no tiene el formato correcto"
                }
        
        # Insertar en BD solo si hay datos válidos
        if processed_data:
            try:
                records = create_bulk(db, processed_data, current_user)
                # Contar cuántos fueron creados vs actualizados usando el atributo temporal
                created_count = sum(1 for r in records if not getattr(r, '_was_updated', False))
                updated_count = sum(1 for r in records if getattr(r, '_was_updated', False))
                
                return {
                    "success": True,
                    "created_records": created_count,
                    "updated_records": updated_count,
                    "total_processed": len(processed_data),
                    "errors": errors if errors else []
                }
            except Exception as db_error:
                # Detectar si es error de tabla no existente
                error_str = str(db_error).lower()
                if 'does not exist' in error_str or 'undefinedtable' in error_str or 'relation' in error_str:
                    db_error_msg = "La tabla de datos no existe en la base de datos. Por favor, ejecuta las migraciones: 'alembic upgrade head'"
                else:
                    db_error_msg = f"Error al guardar en la base de datos: {str(db_error)}"
                errors.append(db_error_msg)
                return {
                    "success": False,
                    "errors": errors,
                    "message": "Error al guardar los datos procesados"
                }
        else:
            # No hay datos válidos para procesar
            return {
                "success": False,
                "errors": errors if errors else ["No se encontraron datos válidos en el archivo"],
                "message": "No se pudieron procesar registros. Verifica el formato del archivo."
            }
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Traceback: {traceback_str}")
        
        # Sanitizar mensajes de error técnicos
        if 'current_user' in error_msg.lower() or 'is not defined' in error_msg.lower():
            error_msg = "Error interno al procesar el archivo. Por favor, contacta al administrador."
        
        return {
            "success": False,
            "errors": [error_msg],
            "message": "Error al procesar el archivo Excel"
        }