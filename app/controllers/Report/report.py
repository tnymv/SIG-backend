from app.models.log.logs import Logs
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import func
from app.exports.excel_exporter import ExcelExporter
from io import BytesIO
        
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


def export_logs_to_excel_controller(db: Session, date_start: str, date_finish: str, name_entity: str, user_info: dict = None):
    """
    Exporta logs a Excel con formato profesional
    
    Args:
        db: Sesión de base de datos
        date_start: Fecha de inicio (formato ISO)
        date_finish: Fecha de fin (formato ISO)
        name_entity: Nombre de la entidad
        user_info: Información del usuario (opcional)
    
    Returns:
        BytesIO: Buffer con el archivo Excel generado
    """
    try:
        start_date = datetime.fromisoformat(date_start.replace('Z', '+00:00'))
        finish_date = datetime.fromisoformat(date_finish.replace('Z', '+00:00'))

        if start_date > finish_date:
            raise HTTPException(
                status_code=400,
                detail="La fecha de inicio debe ser anterior a la fecha final"
            )

        # Consultar logs con los mismos filtros que get_logs_detail_controller
        logs = db.query(Logs).filter(
            Logs.entity == name_entity,
            Logs.created_at >= start_date,
            Logs.created_at <= finish_date
        ).order_by(Logs.created_at.desc()).all()

        if not logs:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron registros para exportar"
            )

        # Preparar filtros para el exportador
        filters = {
            'date_start': date_start,
            'date_finish': date_finish,
            'name_entity': name_entity
        }

        # Generar Excel usando el exportador
        exporter = ExcelExporter()
        excel_buffer = exporter.export_logs(
            logs=logs,
            filters=filters,
            user_info=user_info
        )

        return excel_buffer

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de fecha inválido. Use formato ISO (YYYY-MM-DD). Error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al exportar logs a Excel: {str(e)}"
        )