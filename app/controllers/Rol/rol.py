from app.models.permissions.permissions import Permissions
from app.utils.response import existence_response_dict
from app.schemas.user.user import UserLogin
from app.schemas.rol.rol import RolCreate
from app.utils.logger import create_log
from app.models.rol.rol import Rol
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException
from datetime import datetime
from typing import Optional

def get_all(db: Session, page: int, limit: int, search: Optional[str] = None):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")

    offset = (page - 1) * limit
    
    # Construir query base
    query = db.query(Rol)
    
    # Aplicar búsqueda si se proporciona
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        # Buscar en name y description (coalesce maneja NULL como cadena vacía)
        query = query.filter(
            or_(
                func.lower(Rol.name).like(search_term),
                func.lower(func.coalesce(Rol.description, '')).like(search_term)
            )
        )
    
    # Contar total antes de paginar
    total = query.count()
    
    # Aplicar paginación
    roles = query.offset(offset).limit(limit).all()

    # Si no hay resultados pero hay búsqueda, no es un error, solo no hay coincidencias
    if not roles and not search:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "No hay roles disponibles"),
            headers={"X-Error": "No hay roles disponibles"}
        )
    return roles, total

def get_by_id(db: Session, rol_id: int):
    rol = db.query(Rol).filter(Rol.id_rol == rol_id).first()

    if not rol:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El rol no existe"),
            headers={"X-Error": "El rol no existe"}
        )

    todos_los_permisos = db.query(Permissions).all()
    
    permisos_dict = {}
    for permiso in todos_los_permisos:
        nombre_key = permiso.name.lower().replace(" ", "_")
        permisos_dict[nombre_key] = False

    for permiso in rol.permissions:
        nombre_key = permiso.name.lower().replace(" ", "_")
        permisos_dict[nombre_key] = True

    response = {
        "rol_id": rol.id_rol,
        "rol_name": rol.name,
        "permisos": permisos_dict
    }
    return response


def create(db: Session, data: RolCreate,current_user: UserLogin):
    existing = db.query(Rol).filter(Rol.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El rol ya existe"),
            headers={"X-error": "El rol ya existe"}
        )

    new_rol = Rol(
        name=data.name,
        description=data.description,
        status=data.status,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_rol)
    db.flush()  # Para obtener el ID antes de commit

    # Asociar permisos si existen
    if data.permission_ids:
        permisos = db.query(Permissions).filter(
            Permissions.id_permissions.in_(data.permission_ids)
        ).all()

        if not permisos:
            raise HTTPException(status_code=404, detail="No se encontraron los permisos indicados")

        new_rol.permissions.extend(permisos)

    db.commit()
    db.refresh(new_rol)
    create_log(
        db,
        user_id=current_user.id_user,
        action = "CREATE",
        entity = "Employee",
        entity_id=new_rol.id_rol,
        description=f"El usuario {current_user.user} creó el rol {new_rol.id_rol}"
    ) 
    return new_rol