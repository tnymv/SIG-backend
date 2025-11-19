from fastapi import HTTPException, APIRouter
from app.models.interventions.interventions import Interventions
from app.models.tanks.tanks import Tank
from app.models.pipes.pipes import Pipes
from app.models.connection.connections import Connection
from app.models.intervention_entities.intervention_entities import Intervention_entities
from typing import List, Optional
from datetime import datetime 
from app.schemas.interventions.interventions import InterventionsBase, InterventionsResponse, InterventionsUpdate, InterventionsCreate
from app.db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.logger import create_log
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin

def get_all(db: Session, page: int, limit: int, search: Optional[str] = None):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
    
    offset = (page - 1) * limit
    
    query = db.query(Interventions)
    
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        query = query.filter(
            func.lower(Interventions.description).like(search_term)
        )
    
    total = query.count()
    
    interventions = query.offset(offset).limit(limit).all()
    
    if not interventions and not search:
        raise HTTPException(
            status_code = 404, 
            detail=existence_response_dict(False, "No hay intervenciones registradas"),
            headers={"X-Error": "No hay intervenciones registradas"}
        )
    
    return interventions, total

def get_by_id(db: Session, intervention_id: int):
    intervention = db.query(Interventions).filter(Interventions.id_interventions == intervention_id).first()
    
    if not intervention:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "La intervención no existe")
        )
    
    return intervention

def create(db: Session, data: InterventionsCreate, current_user: UserLogin):
    entity_ids = [data.id_tank, data.id_pipes, data.id_connection]
    provided_ids = [id for id in entity_ids if id is not None]
    
    if len(provided_ids) == 0:
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar al menos un ID de entidad (id_tank, id_pipes o id_connection)",
            headers={"X-Error": "ID de entidad requerido"}
        )
    
    if len(provided_ids) > 1:
        raise HTTPException(
            status_code=400,
            detail="Solo puede proporcionar un ID de entidad a la vez",
            headers={"X-Error": "Múltiples IDs de entidad"}
        )
    
    entity_type = ""
    entity_id = None
    
    if data.id_tank:
        entity = db.query(Tank).filter(Tank.id_tank == data.id_tank).first()
        entity_type = "tanque"
        entity_id = data.id_tank
        if not entity:
            raise HTTPException(status_code=404, detail="El tanque no existe")
            
    elif data.id_pipes:
        entity = db.query(Pipes).filter(Pipes.id_pipes == data.id_pipes).first()
        entity_type = "tubería"
        entity_id = data.id_pipes
        if not entity:
            raise HTTPException(status_code=404, detail="La tubería no existe")
            
    elif data.id_connection:
        entity = db.query(Connection).filter(Connection.id_connection == data.id_connection).first()
        entity_type = "conexión"
        entity_id = data.id_connection
        if not entity:
            raise HTTPException(status_code=404, detail="La conexión no existe")

    existing_intervention = db.query(Interventions).filter(
        Interventions.description == data.description,
        Interventions.start_date == data.start_date
    ).first()
    
    if existing_intervention:
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "Ya existe una intervención idéntica"),
            headers={"X-Error": "La intervención ya existe"}
        )
    
    try:

        new_intervention = Interventions(
            description=data.description,
            start_date=data.start_date,
            end_date=data.end_date,
            status=data.status,
            photography=data.photography,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(new_intervention)
        db.commit()
        db.refresh(new_intervention)

        intervention_entity = Intervention_entities(
            d_interventions=new_intervention.id_interventions,
            id_tank=data.id_tank,
            id_pipes=data.id_pipes,
            id_connection=data.id_connection
        )
        db.add(intervention_entity)
        db.commit()
        db.refresh(new_intervention)

        create_log(
            db,
            user_id=current_user.id_user,
            action="CREATE",
            entity="Intervención",
            entity_id=new_intervention.id_interventions,
            description=f"El usuario {current_user.user} creó intervención en {entity_type} ID {entity_id}: {data.description}"
        )
        
        return new_intervention
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear la intervención: {str(e)}",
            headers={"X-Error": f"Error al crear la intervención: {str(e)}"}
        )

def update(db: Session, intervention_id: int, data: InterventionsUpdate, current_user: UserLogin):
    intervention = db.query(Interventions).filter(Interventions.id_interventions == intervention_id).first()
    
    if not intervention:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "La intervención no existe"),
            headers={"X-Error": "La intervención no existe"}
        )
    
    try:
        for field, value in data.dict(exclude_unset=True).items():
            setattr(intervention, field, value)
        
        intervention.updated_at = datetime.now()
        db.commit()
        db.refresh(intervention)

        create_log(
            db,
            user_id=current_user.id_user,
            action="UPDATE",
            entity="Intervenciones",
            entity_id=intervention.id_interventions,
            description=f"El usuario {current_user.user} actualizó la intervención: {intervention.description}"
        )
        
        return intervention
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar la intervención: {str(e)}",
            headers={"X-Error": f"Error al actualizar la intervención: {str(e)}"}
        )

def toggle_state(db: Session, intervention_id: int, current_user: UserLogin):
    intervention = db.query(Interventions).filter(Interventions.id_interventions == intervention_id).first()
    
    if not intervention:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "La intervención no existe"),
            headers={"X-Error": "La intervención no existe"}
        )
    
    try:
        intervention.status = not intervention.status
        intervention.updated_at = datetime.now()
        db.commit()
        db.refresh(intervention)

        action_text = "activó" if intervention.status else "desactivó"
        create_log(
            db,
            user_id=current_user.id_user,
            action="TOGGLE",
            entity="Intervenciones",
            entity_id=intervention.id_interventions,
            description=f"El usuario {current_user.user} {action_text} la intervención: {intervention.description}"
        )
        
        return intervention
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al desactivar la intervención: {str(e)}",
            headers={"X-Error": f"Error al desactivar la intervención: {str(e)}"}
        )