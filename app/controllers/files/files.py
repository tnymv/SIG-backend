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

# router = APIRouter(prefix='/files', tags=['Files'])

# @router.get('', response_model=List[FilesResponse])
# async def get_files(
#     page: int = 1, limit: int = 5,
#     db: Session = Depends (get_db),
#     current_user: UserLogin = Depends(get_current_active_user)
#     ):

#     try:
#         offset = (page - 1) * limit
#         if page < 1 or limit < 1:
#             raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
#         files = db.query(Files).offset(offset).limit(limit).all()

#         create_log(
#             db,
#             user_id = current_user.id_user,
#             action= "READ",
#             entity= "Files",
#             description= f"El usuario {current_user.user} accedió a la lista de archivos"
#         )

#         return success_response([FilesResponse.model_validate(emp).model_dump(mode="json") for emp in files])
#     except Exception as e:
#         return error_response(f"Error al obtener los archivos: {str(e)}")
    
# @router.post('', response_model=FilesResponse)
# async def create_files(
#     files_data: FilesBase,
#     db: Session = Depends(get_db),
#     current_user: UserLogin = Depends(get_current_active_user)
#     ):
#     if db.query(Files).filter(Files.taxpayer == files_data.cologne).first():
#         raise HTTPException(
#             status_code=409,
#             detail=existence_response_dict(True, "El archivo ya existe"),
#             headers={"X-Error": "El archivo ya existe"}
#         )
    
#     try: 
#         new_files = Files(
#             taxpayer = files_data.taxpayer,
#             cologne = files_data.cologne,
#             cat_service = files_data.cat_service,
#             canon = files_data.canon,
#             excess = files_data.excess,
#             total = files_data.total,
#             created_at=datetime.now(),
#             updated_at=datetime.now()
#         )

#         db.add(new_files)
#         db.commit()
#         db.refresh(new_files)

#         create_log(
#             db,
#             user_id = current_user.id_user,
#             action= "CREATE",
#             entity= "Files",
#             entity_id= new_files.id,
#             description= f"El usuario {current_user.user} creó el documento {new_files.taxpayer} {new_files.cologne}"
#         )
#         return success_response(FilesResponse.model_validate(new_files).model_dump(mode="json"))
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=error_response(f"Error al crear el empleado: {str(e)}").body.decode(),
#             headers={"X-Error": f"Error al crear el empleado: {str(e)}"}
#         )

# @router.put('/{files_id}', response_model=FilesResponse)
# async def update_files(
#     files_id: int,
#     files_data: FilesUpdate,
#     db: Session = Depends(get_db),
#     current_user: UserLogin = Depends(get_current_active_user)
# ):
#     files = db.query(Files).filter(Files.id == files_id).first()
#     if not files:
#         raise HTTPException(
#             status_code=404,
#             detail=existence_response_dict(False, "El archivo no existe"),
#             headers={"X-Error": "El archivo no existe"}
#         )
#     try: 
#         if files_data.taxpayer is not None:
#             files.taxpayer = files_data.taxpayer
        
#         if files_data.cologne is not None:
#             files.cologne = files_data.cologne

#         if files_data is not None:
#             files.cat_service = files_data.cat_service
        
#         if files_data is not None:
#             files.canon = files_data.canon

#         if files_data is not None:
#             files.excess = files_data.excess
        
#         if files_data is not None:
#             files.total = files_data.total

#         files.updated_at = datetime.now()

#         db.commit()
#         db.refresh(files)

#         create_log(
#             db,
#             user_id = current_user.id_user,
#             action= "UPDATE",
#             entity= "Employee",
#             entity_id= files.id,
#             description= f"El usuario {current_user.user} actualizó el archivo {files.taxpayer} {files.cologne}"
#         )

#         return success_response(FilesResponse.model_validate(files).model_dump(mode="json"))

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=error_response(f"Error al actualizar el archivo: {str(e)}").body.decode(),
#             headers={"X-Error": f"Error al actualizar el archivo: {str(e)}"}
#         )
    
# @router.delete('/{files_id}', response_model=FilesResponse)
# async def delete_files(
#     files_id: int,
#     db: Session = Depends(get_db),
#     current_user: UserLogin = Depends(get_current_active_user)
# ):
    
#     files = db.query(Files).filter(Files.id== files_id).first()
#     if not files:
#         raise HTTPException(
#             status_code=404,
#             detail=existence_response_dict(False, "El archivo no existe"),
#             headers={"X-Error": "El archivo no existe"}
#         )

#     try:
#         new_status = not files.status
#         files.status = new_status
#         files.updated_at = datetime.now()
#         db.commit()
#         db.refresh(files)

#         action_text = "activó" if new_status else "desactivó"
#         create_log(
#             db,
#             user_id = current_user.id_user,
#             action= "UPDATE",
#             entity= "Employee",
#             entity_id= files.id,
#             description= f"El usuario {current_user.user} {action_text} el empleado {files.taxpayer} {files.cologne}"
#         )

#         return success_response(f"Archivo {'activado' if new_status else 'desactivado'} exitosamente")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=error_response(f"Error al desactivar el archivo: {str(e)}").body.decode(),
#             headers={"X-Error": f"Error al desactivar el archivo: {str(e)}"}
#         )

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


def create(db: Session, data, current_user):
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


def update(db: Session, file_id: int, data, current_user):
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


def toggle_state(db: Session, file_id: int, current_user):
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