from fastapi import HTTPException, APIRouter
from app.models.interventions.interventions import Interventions
from app.models.tanks.tanks import Tank
from app.models.pipes.pipes import Pipes
from app.models.connection.connections import Connection
from app.models.intervention_entities.intervention_entities import Intervention_entities
from typing import List
from datetime import datetime 
from app.schemas.interventions.interventions import InterventionsBase, InterventionsResponse, InterventionsUpdate, InterventionsCreate
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.logger import create_log
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin

# router = APIRouter(prefix='/interventions', tags=['Interventions'])

# @router.get('', response_model=List[InterventionsResponse])
# async def get_interventions(
#     page: int = 1, limit: int = 5, 
#     db: Session = Depends(get_db),
#     current_user: UserLogin = Depends(get_current_active_user)
# ):
#     try:
#         if page < 1 or limit < 1:
#             raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
#         offset = (page - 1) * limit
#         interventions = db.query(Interventions).offset(offset).limit(limit).all()
        
#         create_log(
#             db,
#             user_id=current_user.id_user,
#             action="READ",
#             entity="Interventions",
#             description=f"El usuario {current_user.user} accedió a la lista de intervenciones"
#         )

#         return success_response([InterventionsResponse.model_validate(emp).model_dump(mode="json") for emp in interventions])
#     except Exception as e:
#         return error_response(f"Error al obtener las intervenciones: {str(e)}")
    
# @router.get('/{intervention_id}', response_model=InterventionsResponse)
# async def get_intervention_by_id(
#     intervention_id: int,
#     db: Session = Depends(get_db),
#     current_user: UserLogin = Depends(get_current_active_user)
# ):
#     intervention = db.query(Interventions).filter(Interventions.id_interventions == intervention_id).first()
    
#     if not intervention:
#         raise HTTPException(status_code=404, detail="Intervención no encontrada")
    
#     entity_info = db.query(Intervention_entities).filter(
#         Intervention_entities.id_interventions == intervention_id
#     ).first()
    
#     return success_response(InterventionsResponse.model_validate(intervention).model_dump(mode="json"))

# @router.post('', response_model=InterventionsResponse)
# async def create_interventions(
#     interventions_data: InterventionsCreate, 
#     db: Session = Depends(get_db),
#     current_user: UserLogin = Depends(get_current_active_user)
# ):
#     #este metodo sive para validaer que solo se ingrese un id
#     entity_ids = [interventions_data.id_tank, interventions_data.id_pipes, interventions_data.id_connection]
#     provided_ids = [id for id in entity_ids if id is not None]
    
#     if len(provided_ids) == 0:
#         raise HTTPException(
#             status_code=400,
#             detail="Debe proporcionar al menos un ID de entidad (id_tank, id_pipes o id_connection)",
#             headers={"X-Error": "ID de entidad requerido"}
#         )
    
#     if len(provided_ids) > 1:
#         raise HTTPException(
#             status_code=400,
#             detail="Solo puede proporcionar un ID de entidad a la vez",
#             headers={"X-Error": "Múltiples IDs de entidad"}
#         )
    
#     entity = None
#     entity_type = ""
#     entity_id = None
    
#     if interventions_data.id_tank:
#         entity = db.query(Tank).filter(Tank.id_tank == interventions_data.id_tank).first()
#         entity_type = "tanque"
#         entity_id = interventions_data.id_tank
#         if not entity:
#             raise HTTPException(status_code=404, detail="El tanque no existe")
            
#     elif interventions_data.id_pipes:
#         entity = db.query(Pipes).filter(Pipes.id_pipes == interventions_data.id_pipes).first()
#         entity_type = "tubería"
#         entity_id = interventions_data.id_pipes
#         if not entity:
#             raise HTTPException(status_code=404, detail="La tubería no existe")
            
#     elif interventions_data.id_connection:
#         entity = db.query(Connection).filter(Connection.id_connection == interventions_data.id_connection).first()
#         entity_type = "conexión"
#         entity_id = interventions_data.id_connection
#         if not entity:
#             raise HTTPException(status_code=404, detail="La conexión no existe")
    
#     # Verificamos si existe una misma intervencion 
#     existing_intervention = db.query(Interventions).filter(
#         Interventions.description == interventions_data.description,
#         Interventions.start_date == interventions_data.start_date
#     ).first()
    
#     if existing_intervention:
#         raise HTTPException(
#             status_code=409,
#             detail=existence_response_dict(True, "Ya existe una intervención idéntica"),
#             headers={"X-Error": "La intervención ya existe"}
#         )
    
#     try: 
#         new_intervention = Interventions(
#             description=interventions_data.description,
#             start_date=interventions_data.start_date,
#             end_date=interventions_data.end_date,
#             status=interventions_data.status,
#             photography=interventions_data.photography,
#             created_at=datetime.now(),
#             updated_at=datetime.now()
#         )

#         db.add(new_intervention)
#         db.commit()
#         db.refresh(new_intervention)

#         # Se crea la realacion con la tabla puente
#         intervention_entity = Intervention_entities(
#             id_interventions=new_intervention.id_interventions, 
#             id_tank=interventions_data.id_tank,
#             id_pipes=interventions_data.id_pipes,
#             id_connection=interventions_data.id_connection
#         )
#         db.add(intervention_entity)
#         db.commit()
#         db.refresh(new_intervention)

#         # log
#         create_log(
#             db,
#             user_id=current_user.id_user,
#             action="CREATE",
#             entity="Intervención",
#             entity_id=new_intervention.id_interventions,
#             description=f"El usuario {current_user.user} creó intervención en {entity_type} ID {entity_id}: {interventions_data.description}"
#         )

#         return success_response(InterventionsResponse.model_validate(new_intervention).model_dump(mode="json"))
        
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=error_response(f"Error al crear la Intervención: {str(e)}").body.decode(),
#             headers={"X-Error": f"Error al crear la Intervención: {str(e)}"}
#         )

# @router.put('/{interventions_id}', response_model=InterventionsResponse)
# async def update_interventions(
#     interventions_id: int,  # ← Corregí el nombre del parámetro
#     interventions_data: InterventionsUpdate,
#     db: Session = Depends(get_db),
#     current_user: UserLogin = Depends(get_current_active_user)
# ):
#     interventions = db.query(Interventions).filter(Interventions.id_interventions == interventions_id).first()
#     if not interventions:
#         raise HTTPException(
#             status_code=404,
#             detail=existence_response_dict(False, "La intervención no existe"),  # ← Corregí el mensaje
#             headers={"X-Error": "La intervención no existe"}
#         )
    
#     try: 
#         if interventions_data.description is not None:
#             interventions.description = interventions_data.description
        
#         if interventions_data.start_date is not None:
#             interventions.start_date = interventions_data.start_date
        
#         if interventions_data.end_date is not None:
#             interventions.end_date = interventions_data.end_date

#         if interventions_data.status is not None:
#             interventions.status = interventions_data.status
        
#         if interventions_data.photography is not None:
#             interventions.photography = interventions_data.photography
        
#         interventions.updated_at = datetime.now()

#         db.commit()
#         db.refresh(interventions)

#         create_log(
#             db,
#             user_id=current_user.id_user,
#             action="UPDATE",
#             entity="Intervenciones",
#             entity_id=interventions.id_interventions,
#             description=f"El usuario {current_user.user} actualizó la intervención: {interventions.description}"  # ← Corregí la descripción
#         )

#         return success_response(InterventionsResponse.model_validate(interventions).model_dump(mode="json"))

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=error_response(f"Error al actualizar la intervención: {str(e)}").body.decode(),
#             headers={"X-Error": f"Error al actualizar la intervención: {str(e)}"}
#         )

# @router.delete('/{interventions_id}')  # ← Removí response_model porque devuelves string
# async def delete_interventions(
#     interventions_id: int,
#     db: Session = Depends(get_db),
#     current_user: UserLogin = Depends(get_current_active_user)
# ):
#     interventions = db.query(Interventions).filter(Interventions.id_interventions == interventions_id).first()
#     if not interventions:
#         raise HTTPException(
#             status_code=404,
#             detail=existence_response_dict(False, "La intervención no existe"),
#             headers={"X-Error": "La intervención no existe"}
#         )
    
#     try:
#         new_status = not interventions.status
#         interventions.status = new_status
#         interventions.updated_at = datetime.now()
#         db.commit()
#         db.refresh(interventions)

#         action_text = "activó" if new_status else "desactivó"
#         create_log(
#             db,
#             user_id=current_user.id_user,
#             action="UPDATE",
#             entity="Intervenciones",
#             entity_id=interventions.id_interventions,
#             description=f"El usuario {current_user.user} {action_text} la intervención: {interventions.description}"  # ← Corregí la descripción
#         )
        
#         return success_response(f"Intervención {'activada' if new_status else 'desactivada'} exitosamente")  # ← Corregí el mensaje
    
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=error_response(f"Error al desactivar la intervención: {str(e)}").body.decode(),
#             headers={"X-Error": f"Error al desactivar la intervención: {str(e)}"}
#         )

def get_all(db: Session, page: int, limit: int, current_user: UserLogin):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
    
    offset = (page - 1) * limit
    interventions = db.query(Interventions).offset(offset).limit(limit).all()
    
    create_log(
        db,
        user_id=current_user.id_user,
        action="READ",
        entity="Interventions",
        description=f"El usuario {current_user.user} accedió a la lista de intervenciones"
    )
    
    return interventions

def get_by_id(db: Session, intervention_id: int):
    intervention = db.query(Interventions).filter(Interventions.id_interventions == intervention_id).first()
    
    if not intervention:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "La intervención no existe")
        )
    
    return intervention

def create(db: Session, data: InterventionsCreate, current_user: UserLogin):
    # Validar que solo se proporcione un ID de entidad
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
    
    # Validar que la entidad exista
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
    
    # Verificar si existe una intervención idéntica
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
        # Crear nueva intervención
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
        
        # Crear relación con la tabla puente
        intervention_entity = Intervention_entities(
            id_interventions=new_intervention.id_interventions,
            id_tank=data.id_tank,
            id_pipes=data.id_pipes,
            id_connection=data.id_connection
        )
        db.add(intervention_entity)
        db.commit()
        db.refresh(new_intervention)
        
        # Crear log
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
        # Actualizar campos proporcionados
        for field, value in data.dict(exclude_unset=True).items():
            setattr(intervention, field, value)
        
        intervention.updated_at = datetime.now()
        db.commit()
        db.refresh(intervention)
        
        # Crear log
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
        
        # Crear log
        action_text = "activó" if intervention.status else "desactivó"
        create_log(
            db,
            user_id=current_user.id_user,
            action="UPDATE",
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