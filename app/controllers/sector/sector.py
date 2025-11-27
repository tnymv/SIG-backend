from fastapi import HTTPException
from app.models.sector.sector import Sector
from typing import Optional
from datetime import datetime
from app.schemas.sector.sector import SectorBase, SectorUpdate
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.utils.response import existence_response_dict
from app.utils.logger import create_log
from app.schemas.user.user import UserLogin

def get_all(db: Session, page: int, limit: int, search: Optional[str]=None):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
    
    offset = (page - 1 ) * limit
    
    query = db.query(Sector)
    
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Sector.name).like(search_term),
                func.lower(func.coalesce(Sector.description, '')).like(search_term)
            )
        )
    total = query.count()
    
    sectors = query.order_by(Sector.id_sector.desc()).offset(offset).limit(limit).all()
    
    if not sectors and not search:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "No hay sectores disponibles"),
            headers={"X-Error": "No hay sectores disponibles"}
        )
    
    sector_list = [
        {
            "id_sector": s.id_sector,
            "name": s.name,
            "description": s.description,
            "active": s.active,
            "created_at": s.created_at,
            "updated_at": s.updated_at
        }
        for s in sectors
    ]
    
    return sector_list, total

def get_by_id(db: Session, sector_id: int):
    sector = db.query(Sector).filter(Sector.id_sector == sector_id).first()
    if not sector:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "Sector no encontrado"),
            headers={"X-Error": "Sector no encontrado"}
        )
        
    sector_list = {
        "id_sector": sector.id_sector,
        "name": sector.name,
        "description": sector.description,
        "active": sector.active,
        "created_at": sector.created_at,
        "updated_at": sector.updated_at
    }
    return sector_list

def create(db: Session, sector_data: SectorBase, current_user: UserLogin):
    existing_sector = db.query(Sector).filter(Sector.name == sector_data.name).first()
    if existing_sector:
        raise HTTPException(
            status_code=400,
            detail=existence_response_dict(False, "El sector con este nombre ya existe"),
            headers={"X-Error": "El sector con este nombre ya existe"}
        )
    
    try:
        new_sector = Sector(
            name=sector_data.name,
            description=sector_data.description,
            active=sector_data.active,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(new_sector)
        db.commit()
        db.refresh(new_sector)
        
        sector_list = {
            "id_sector": new_sector.id_sector,
            "name": new_sector.name,
            "description": new_sector.description,
            "active": new_sector.active,
            "created_at": new_sector.created_at,
            "updated_at": new_sector.updated_at
        }
        
        create_log(
            db, 
            user_id=current_user.id_user,
            action = "CREATE",
            entity = "Sector",
            entity_id= new_sector.id_sector,
            description=f"El usuario {current_user.user} creó el sector {new_sector.name}"
        )
        
        return sector_list
    except Exception as e: 
        db.rollback()
        raise HTTPException(
            status_code = 500,
            detail=f"Error al crear el sector: {str(e)}"
        )

def update(db: Session, sector_id: int, sector_data: SectorUpdate, current_user: UserLogin):
    sector = db.query(Sector).filter(Sector.id_sector == sector_id).first()
    
    if not sector:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "Sector no encontrado"),
            headers={"X-Error": "Sector no encontrado"}
        )
    
    try:
        update_sector = sector_data.dict(exclude_unset=True)
        
        for field, value in update_sector.items():
            setattr(sector, field, value)
            
        sector.updated_at = datetime.now()
        
        db.commit()
        db.refresh(sector)
        
        sector_list = {
            "id_sector": sector.id_sector,
            "name": sector.name,
            "description": sector.description,
            "active": sector.active,
            "created_at": sector.created_at,
            "updated_at": sector.updated_at
        }
        
        create_log(
            db,
            user_id=current_user.id_user,
            action = "UPDATE",
            entity = "Sector",
            entity_id= sector.id_sector,
            description=f"El usuario {current_user.user} actualizó el sector {sector.name}"
        )
        
        return sector_list
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar el sector: {str(e)}"
        )
        
def toggle_state(db: Session, sector_id: int, current_user: UserLogin):
    sector = db.query(Sector).filter(Sector.id_sector == sector_id).first()
    
    if not sector:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "Sector no encontrado"),
            headers={"X-Error": "Sector no encontrado"}
        )
    
    sector.active = not sector.active
    sector.updated_at = datetime.now()
    
    db.commit()
    db.refresh(sector)
    
    status = ""
    if sector.active is False:
        status = "inactivo"
    else:
        status = "activo"
    create_log(
        db,
        user_id=current_user.id_user,
        action = "TOGGLE_STATE",
        entity = "Sector",
        entity_id= sector.id_sector,
        description=f"El usuario {current_user.user} cambió el estado del sector {sector.name} a {status}"
    )
    return sector