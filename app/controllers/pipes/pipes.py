from fastapi import HTTPException, APIRouter
from app.models.pipes.pipes import Pipes
from app.models.tanks.tanks import Tank
from typing import List
from datetime import datetime
from app.schemas.pipes.pipes import PipesBase, PipesResponse,PipesResponseCreate, PipesUpdate, TankSimple
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.utils.response import success_response, error_response, existence_response_dict
from app.utils.logger import create_log
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin
from sqlalchemy.orm import joinedload
from sqlalchemy import func

router = APIRouter(prefix='/pipes', tags=['Pipes'])

@router.get('', response_model=List[PipesResponse])
async def get_pipes(
    page: int = 1, limit: int = 5,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
    ):

    try:
        offset = (page - 1) * limit
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
        
        offset = (page - 1) * limit
        pipes = db.query(
            Pipes,
            func.ST_X(Pipes.coordinates).label('longitude'),
            func.ST_Y(Pipes.coordinates).label('latitude')
        ).options(joinedload(Pipes.tanks)) \
        .offset(offset).limit(limit).all()


        if not pipes:
            return success_response([])

        pipes_response = []
        for pipe, longitude, latitude in pipes:
            pipe_response = PipesResponse(
                id_pipes=pipe.id_pipes,
                material=pipe.material,
                diameter=pipe.diameter,
                status=pipe.status,
                size=pipe.size,
                installation_date=pipe.installation_date,
                latitude=latitude,
                longitude=longitude,
                observations=pipe.observations,
                created_at=pipe.created_at,
                updated_at=pipe.updated_at,
                tanks=[TankSimple(id_tank=t.id_tank, name=t.name) for t in pipe.tanks]
            )
            
            pipes_response.append(pipe_response.model_dump(mode="json"))

        create_log(
            db,
            user_id=current_user.id_user,
            action="READ",
            entity="Pipes",
            description=f"El usuario {current_user.user} accedió a la lista de tuberías"
        )
        return success_response(pipes_response)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener las tuberías: {str(e)}",
            headers={"X-Error": f"Error al obtener las tuberías: {str(e)}"}
        )
@router.get('/{pipe_id}', response_model=PipesResponse)
async def get_pipe_by_id(
    pipe_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        result = db.query(
            Pipes,
            func.ST_X(Pipes.coordinates).label('longitude'),
            func.ST_Y(Pipes.coordinates).label('latitude')
        ).options(joinedload(Pipes.tanks)) \
        .filter(Pipes.id_pipes == pipe_id).first()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=existence_response_dict(False, "La tubería no existe"),
                headers={"X-Error": "La tubería no existe"}
            )
        
        pipe, longitude, latitude = result
        
        pipe_response = PipesResponse(
            id_pipes=pipe.id_pipes,
            material=pipe.material,
            diameter=pipe.diameter,
            status=pipe.status,
            size=pipe.size,
            installation_date=pipe.installation_date,
            latitude=latitude,
            longitude=longitude,
            observations=pipe.observations,
            created_at=pipe.created_at,
            updated_at=pipe.updated_at,
            tanks=[{"id_tank": t.id_tank, "name": t.name} for t in pipe.tanks]
        )
        
        create_log(
            db,
            user_id=current_user.id_user,
            action="READ",
            entity="Pipes",
            description=f"El usuario {current_user.user} consultó la tubería {pipe.material} (ID: {pipe_id})"
        )
        return success_response(pipe_response.model_dump(mode="json"))
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener la tubería: {str(e)}",
            headers={"X-Error": f"Error al obtener la tubería: {str(e)}"}
        )

@router.post('', response_model=PipesResponse)
async def create_pipes(
    pipes_data: PipesBase,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
    ):
    if db.query(Pipes).filter(Pipes.material == pipes_data.material).first():
        raise HTTPException(
            status_code=409,
            detail=existence_response_dict(True, "La tubería ya existe"),
            headers={"X-Error": "La tubería ya existe"}
        )
    
    try: 
        new_pipes = Pipes(
            material = pipes_data.material,
            diameter = pipes_data.diameter,
            status = pipes_data.status,
            size = pipes_data.size,
            installation_date = pipes_data.installation_date,
            coordinates=f"SRID=4326;POINT({pipes_data.longitude} {pipes_data.latitude})",
            observations=pipes_data.observations,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Asignar los tanques seleccionados
        for tank_id in pipes_data.tank_ids:
            tank = db.query(Tank).filter(Tank.id_tank == tank_id).first()
            if tank:
                new_pipes.tanks.append(tank)

        db.add(new_pipes)
        db.commit()
        db.refresh(new_pipes)

        pipes_response = PipesResponseCreate(
            id_pipes=new_pipes.id_pipes,
            material=new_pipes.material,
            diameter=new_pipes.diameter,
            status=new_pipes.status,
            size=new_pipes.size,
            installation_date=new_pipes.installation_date,
            latitude=pipes_data.latitude,  
            longitude=pipes_data.longitude,  
            observations=new_pipes.observations,
            created_at=new_pipes.created_at,
            updated_at=new_pipes.updated_at,
            tanks=[TankSimple(id_tank=t.id_tank, name=t.name) for t in new_pipes.tanks]
        )

        create_log(
            db,
            user_id=current_user.id_user,
            action="CREATE",
            entity= "Tubería",
            entity_id= new_pipes.id_pipes,
            description= f"El usuario {current_user.user} creó una nueva tubeía"
        )
        return success_response(pipes_response.model_dump(mode="json"))
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al crear la tubería: {str(e)}"). body.decode(),
            headers={"X-Error": f"Error al crear la tubería: {str(e)}"}
        )
    
@router.put('/{pipe_id}', response_model=PipesResponse)
async def update_pipe(
    pipe_id: int,
    pipe_data: PipesUpdate,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    # Buscar tubería
    pipe = db.query(Pipes).filter(Pipes.id_pipes == pipe_id).first()
    if not pipe:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "La tubería no existe"),
            headers={"X-Error": "La tubería no existe"}
        )

    if pipe_data.material and pipe_data.material != pipe.material:
        existing_pipe = db.query(Pipes).filter(Pipes.material == pipe_data.material).first()
        if existing_pipe:
            raise HTTPException(
                status_code=409,
                detail=existence_response_dict(True, "El material de la tubería ya existe"),
                headers={"X-Error": "El material de la tubería ya existe"}
            )
    
    try:
        # Actualizar solo los campos no nuloss
        if pipe_data.material is not None:
            pipe.material = pipe_data.material
            
        if pipe_data.diameter is not None:
            pipe.diameter = pipe_data.diameter
            
        if pipe_data.status is not None:
            pipe.status = pipe_data.status
            
        if pipe_data.size is not None:
            pipe.size = pipe_data.size
            
        if pipe_data.installation_date is not None:
            pipe.installation_date = pipe_data.installation_date
        
        if pipe_data.tank_ids is not None:
            pipe.tanks.clear()
            for tank_id in pipe_data.tank_ids:
                tank = db.query(Tank).filter(Tank.id_tank == tank_id).first()
                if tank:
                    pipe.tanks.append(tank)

            
        if pipe_data.latitude is not None and pipe_data.longitude is not None:
            pipe.coordinates = f"SRID=4326;POINT({pipe_data.longitude} {pipe_data.latitude})"
        elif pipe_data.latitude is not None or pipe_data.longitude is not None:
            raise HTTPException(
                status_code=400,
                detail="Ambos campos latitude y longitude deben ser proporcionados juntos.",
                headers={"X-Error": "Campos de coordenadas incompletos"}
            )
            
        if pipe_data.observations is not None:
            pipe.observations = pipe_data.observations
            
        pipe.updated_at = datetime.now()
        
        db.commit()
        db.refresh(pipe)
        
        # Para obtener las coordenadas
        result = db.query(
            Pipes,
            func.ST_X(Pipes.coordinates).label('longitude'),
            func.ST_Y(Pipes.coordinates).label('latitude')
        ).filter(Pipes.id_pipes == pipe.id_pipes).first()
        
        pipe, longitude, latitude = result
        
        pipe_response = PipesResponse(
            id_pipes=pipe.id_pipes,
            material=pipe.material,
            diameter=pipe.diameter,
            status=pipe.status,
            size=pipe.size,
            installation_date=pipe.installation_date,
            latitude=latitude,
            longitude=longitude,
            observations=pipe.observations,
            created_at=pipe.created_at,
            updated_at=pipe.updated_at,
            tanks=[{"id_tank": tank.id_tank, "name": tank.name} for tank in pipe.tanks]
        )
        
        create_log(
            db,
            user_id=current_user.id_user,
            action="PUT",
            entity="Pipes",
            description=f"El usuario {current_user.user} actualizó la tubería {pipe.id_pipes}"
        )
        return success_response(pipe_response.model_dump(mode="json"))

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar la tubería: {str(e)}")
    
@router.delete('/{pipe_id}', response_model=PipesResponse)
async def delete_pipe(
    pipe_id: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    pipe = db.query(Pipes).filter(Pipes.id_pipes == pipe_id).first()
    if not pipe:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "La tubería no existe"),
            headers={"X-Error": "La tubería no existe"}
        )
        
    try:
        pipe.status = not pipe.status
        pipe.updated_at = datetime.now()
        db.commit()
        db.refresh(pipe)
        
        action_description = "activó" if pipe.status else "desactivó"
        create_log(
            db,
            user_id=current_user.id_user,
            action="DELETE",
            entity="Pipes",
            description=f"El usuario {current_user.user} {action_description} la tubería {pipe.id_pipes}"
        )   
        
        status_message = "Tubería activada exitosamente" if pipe.status else "Tubería desactivada exitosamente"
        return success_response(status_message)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=error_response(f"Error al eliminar la tubería: {str(e)}").body.decode(),
            headers={"X-Error": f"Error al eliminar la tubería: {str(e)}"}
        )