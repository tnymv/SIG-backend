from fastapi import HTTPException, APIRouter
from app.models.files.files import Files
from typing import List
from datetime import datetime
from app.schemas.files.files import FilesBase, FilesCreate, FilesResponse,FilesUpdate
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.logger import create_log
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin

def get_all(db: Session, page: int, limit: int):
    offset = (page - 1) * limit
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Página y límite deben ser mayores que 0")
    return db.query(Files).offset(offset).limit(limit).all()


def get_by_id(db: Session, file_id: int):
    file = db.query(Files).filter(Files.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "El archivo no existe"))
    return file


def create(db: Session, data,current_user: UserLogin):
    existing = db.query(Files).filter(Files.taxpayer == data.taxpayer, Files.cologne == data.cologne).first()
    if existing:
        raise HTTPException(status_code=409, detail=existence_response_dict(True, "El archivo ya existe"))

    new_file = Files(
        taxpayer=data.taxpayer,
        cologne=data.cologne,
        cat_service=data.cat_service,
        canon=data.canon,
        excess=data.excess,
        total=data.total,
        status=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    create_log(
        db,
        user_id=current_user.id_user,
        action="CREATE",
        entity="Files",
        entity_id=new_file.id,
        description=f"El usuario {current_user.user} creó el archivo {new_file.taxpayer} {new_file.cologne}"
    )

    return new_file


def update(db: Session, file_id: int, data,current_user: UserLogin):
    file = db.query(Files).filter(Files.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "El archivo no existe"))

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(file, field, value)

    file.updated_at = datetime.now()
    db.commit()
    db.refresh(file)

    create_log(
        db,
        user_id=current_user.id_user,
        action="UPDATE",
        entity="Files",
        entity_id=file.id,
        description=f"El usuario {current_user.user} actualizó el archivo {file.taxpayer} {file.cologne}"
    )

    return file


def toggle_state(db: Session, file_id: int, current_user: UserLogin):
    file = db.query(Files).filter(Files.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail=existence_response_dict(False, "El archivo no existe"))

    file.status = not file.status
    file.updated_at = datetime.now()
    db.commit()
    db.refresh(file)

    create_log(
        db,
        user_id=current_user.id_user,
        action="UPDATE",
        entity="Files",
        entity_id=file.id,
        description=f"El usuario {current_user.user} {'activó' if file.status else 'desactivó'} el archivo {file.taxpayer} {file.cologne}"
    )

    return file