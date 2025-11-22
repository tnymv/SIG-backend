from app.models.permissions.permissions import Permissions
from app.utils.response import existence_response_dict
from app.schemas.user.user import UserLogin
from app.schemas.rol.rol import RolCreate, RolUpdate
from app.utils.logger import create_log
from app.models.rol.rol import Rol
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException
from datetime import datetime
from typing import Optional, List, Dict

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
    roles = query.order_by(Rol.id_rol.desc()).offset(offset).limit(limit).all()

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

    # Obtener todos los permisos del rol
    permisos_asignados = [perm.id_permissions for perm in rol.permissions]
    
    response = {
        "id_rol": rol.id_rol,
        "name": rol.name,
        "description": rol.description,
        "status": rol.status,
        "created_at": rol.created_at.isoformat() if rol.created_at else None,
        "updated_at": rol.updated_at.isoformat() if rol.updated_at else None,
        "permission_ids": permisos_asignados,
        "permissions": [
            {
                "id_permissions": perm.id_permissions,
                "name": perm.name,
                "description": perm.description,
                "status": perm.status
            }
            for perm in rol.permissions
        ]
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
        entity = "Rol",
        entity_id=new_rol.id_rol,
        description=f"El usuario {current_user.user} creó el rol {new_rol.name}"
    ) 
    return new_rol

def update(db: Session, rol_id: int, data: RolUpdate, current_user: UserLogin):
    rol = db.query(Rol).filter(Rol.id_rol == rol_id).first()
    
    if not rol:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "El rol no existe"),
            headers={"X-Error": "El rol no existe"}
        )
    
    # Actualizar campos básicos si se proporcionan
    if data.name is not None:
        # Verificar que el nombre no esté en uso por otro rol
        existing = db.query(Rol).filter(Rol.name == data.name, Rol.id_rol != rol_id).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=existence_response_dict(True, "Ya existe un rol con ese nombre"),
                headers={"X-Error": "El rol ya existe"}
            )
        rol.name = data.name
    
    if data.description is not None:
        rol.description = data.description
    
    if data.status is not None:
        rol.status = data.status
    
    # Actualizar permisos si se proporcionan (incluso si es una lista vacía)
    if data.permission_ids is not None:
        # Debug: verificar qué se está recibiendo
        print(f"Actualizando permisos para rol {rol_id}: {data.permission_ids}")
        
        # Si la lista está vacía, limpiar todos los permisos
        if len(data.permission_ids) == 0:
            print("Limpiando todos los permisos del rol")
            rol.permissions.clear()
            db.flush()
        else:
            # Obtener los permisos solicitados
            permisos = db.query(Permissions).filter(
                Permissions.id_permissions.in_(data.permission_ids)
            ).all()
            
            print(f"Permisos encontrados en BD: {[p.id_permissions for p in permisos]}")
            
            # Verificar que se encontraron todos los permisos solicitados
            permisos_encontrados_ids = {perm.id_permissions for perm in permisos}
            permisos_solicitados_ids = set(data.permission_ids)
            
            if permisos_encontrados_ids != permisos_solicitados_ids:
                permisos_faltantes = permisos_solicitados_ids - permisos_encontrados_ids
                raise HTTPException(
                    status_code=404, 
                    detail=f"Los siguientes permisos no fueron encontrados: {list(permisos_faltantes)}"
                )
            
            # Limpiar permisos existentes y asignar los nuevos
            print(f"Permisos actuales antes de limpiar: {[p.id_permissions for p in rol.permissions]}")
            rol.permissions.clear()
            db.flush()  # Asegurar que se eliminen las relaciones anteriores
            rol.permissions.extend(permisos)
            db.flush()  # Asegurar que se agreguen las nuevas relaciones
            print(f"Permisos después de actualizar: {[p.id_permissions for p in rol.permissions]}")
    
    rol.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(rol)
    
    # Recargar los permisos para asegurar que estén actualizados
    db.refresh(rol)
    # Forzar la carga de la relación de permisos
    _ = rol.permissions
    
    create_log(
        db,
        user_id=current_user.id_user,
        action="UPDATE",
        entity="Rol",
        entity_id=rol.id_rol,
        description=f"El usuario {current_user.user} actualizó el rol {rol.name}"
    )
    
    return rol

def get_permissions_grouped(db: Session) -> Dict[str, List[Dict]]:
    """Obtiene todos los permisos activos agrupados por categoría"""
    permisos = db.query(Permissions).filter(Permissions.status == True).all()
    
    # Mapeo de prefijos a categorías
    categoria_map = {
        'tuberias': 'Tuberías',
        'conexiones': 'Conexiones',
        'tanques': 'Tanques',
        'desvios': 'Desvíos',
        'usuarios': 'Usuarios',
        'empleados': 'Empleados',
        'archivos': 'Archivos',
        'roles': 'Roles',
        'fontaneros': 'Fontaneros',
        'intervenciones': 'Intervenciones',
    }
    
    grouped = {}
    
    for permiso in permisos:
        # Extraer categoría del nombre del permiso (ej: "crear_tuberias" -> "tuberias")
        nombre_parts = permiso.name.split('_')
        if len(nombre_parts) >= 2:
            categoria_key = nombre_parts[-1]  # Última parte es la categoría
            categoria_nombre = categoria_map.get(categoria_key, categoria_key.capitalize())
            
            if categoria_nombre not in grouped:
                grouped[categoria_nombre] = []
            
            grouped[categoria_nombre].append({
                "id_permissions": permiso.id_permissions,
                "name": permiso.name,
                "description": permiso.description,
                "status": permiso.status
            })
    
    return grouped