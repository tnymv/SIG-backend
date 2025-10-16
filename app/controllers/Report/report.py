from fastapi import HTTPException, APIRouter
from typing import List
from datetime import datetime
from fastapi import Depends
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.models.log.logs import Logs
from sqlalchemy import func
from app.schemas.log.logs import LogSummaryResponse,LogBase
from app.schemas.user.user import UserLogin
from app.controllers.auth.auth_controller import get_current_active_user


router = APIRouter(prefix = '/report', tags = ['Reports'])

@router.get("/logs/summary", response_model=LogSummaryResponse)
async def get_logs_summary(
    date_start: str, 
    date_finish: str,  
    name_entity: str, 
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        start_date = datetime.fromisoformat(date_start.replace('Z', '+00:00'))
        finish_date = datetime.fromisoformat(date_finish.replace('Z', '+00:00'))
        
        if start_date > finish_date:
            raise HTTPException(
                status_code=400, 
                detail="La fecha de inicio debe ser anterior a la fecha final"
            )

        stats = db.query(
            Logs.action,
            func.count(Logs.log_id).label('count')
        ).filter(
            Logs.entity == name_entity,
            Logs.created_at >= start_date,
            Logs.created_at <= finish_date
        ).group_by(Logs.action).all()
        
        total_logs = sum([stat.count for stat in stats])
        
        if total_logs == 0:
            return {
                "entity": name_entity,
                "date_range": {
                    "start": date_start,
                    "finish": date_finish
                },
                "total_logs": 0,
                "actions_summary": []
            }
        
        # Formatear respuesta
        return {
            "entity": name_entity,
            "date_range": {
                "start": date_start,
                "finish": date_finish
            },
            "total_logs": total_logs,
            "actions_summary": [
                {"action": stat.action, "count": stat.count} 
                for stat in stats
            ]
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de fecha inválido. Use formato ISO (YYYY-MM-DD). Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el resumen: {str(e)}"
        )
        
@router.get("/logs/detail", response_model=List[LogBase])
async def get_logs_detail(
    date_start: str, 
    date_finish: str,  
    name_entity: str,  
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    
    try:
        start_date = datetime.fromisoformat(date_start.replace('Z', '+00:00'))
        finish_date = datetime.fromisoformat(date_finish.replace('Z', '+00:00'))

        if start_date > finish_date:
            raise HTTPException(
                status_code=400, 
                detail="La fecha de inicio debe ser anterior a la fecha final"
            )

        logs = db.query(Logs).filter(
            Logs.entity == name_entity,
            Logs.created_at >= start_date,
            Logs.created_at <= finish_date
        ).order_by(Logs.created_at.desc()).all()  

        if not logs:
            return []

        return [
            {
                "log_id": log.log_id,
                "user_id": log.user_id,
                "action": log.action,
                "entity": log.entity,
                "entity_id": log.entity_id,
                "description": log.description,
                "created_at": log.created_at
            }
            for log in logs
        ]
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de fecha inválido. Use formato ISO (YYYY-MM-DD). Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el reporte detallado: {str(e)}"
        )
        
@router.get("/entities")
async def get_available_entities(
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
    ):
    try:
        entities = db.query(Logs.entity).distinct().filter(Logs.entity.isnot(None)).all()
        return {"entities": [entity[0] for entity in entities]}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener entidades: {str(e)}"
        )