from app.models.permissions.permissions import Permissions
from app.utils.response import existence_response_dict
from app.schemas.rol.rol import RolCreate
from app.models.rol.rol import Rol
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

def get_all(db: Session, page: int, limit: int):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")

    offset = (page - 1) * limit
    roles = db.query(Rol).offset(offset).limit(limit).all()

    if not roles:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "No hay roles disponibles"),
            headers={"X-Error": "No hay roles disponibles"}
        )

    return roles

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

    # 3️⃣ Marcar True solo los que el rol realmente tiene
    for permiso in rol.permissions:
        nombre_key = permiso.name.lower().replace(" ", "_")
        permisos_dict[nombre_key] = True

    response = {
        "id_rol": rol.id_rol,
        "name": rol.name,
        "description": rol.description,
        "status": rol.status,
        "created_at": rol.created_at,
        "updated_at": rol.updated_at,
        "permisos": permisos_dict
    }

    return response


def create(db: Session, data: RolCreate):
    existing = db.query(Rol).filter(Rol.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "El rol ya existe"),
            headers={"X-error": "El rol ya existe"}
        )

    # Crear el nuevo rol
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

    return new_rol