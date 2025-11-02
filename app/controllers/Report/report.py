from app.models.log.logs import Logs
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import func
        
def get_logs_summary_controller(db: Session, date_start: str, date_finish: str, name_entity: str):
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


def get_logs_detail_controller(db: Session, date_start: str, date_finish: str, name_entity: str):
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

        return logs or []
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


def get_available_entities_controller(db: Session):
    try:
        entities = db.query(Logs.entity).distinct().filter(Logs.entity.isnot(None)).all()
        return [entity[0] for entity in entities]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener entidades: {str(e)}"
        )