from fastapi import APIRouter, Depends
from fastapi.responses import Response
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.schemas.log.logs import LogSummaryResponse, LogBase
from app.schemas.user.user import UserLogin
from app.controllers.auth.auth_controller import get_current_active_user
from app.controllers.Report.report import (
    get_logs_summary_controller,
    get_logs_detail_controller,
    get_available_entities_controller,
    export_logs_to_excel_controller,
    report_pipes_by_sector,
    report_interventions_by_pipes,
    report_interventions_by_connections,
    report_sector_comparative,
    report_interventions,
    report_interventions_by_sector,
    report_intervention_frequency,
    report_tanks
)
from fastapi import HTTPException
router = APIRouter(prefix='/report', tags=['Reports'])


@router.get("/logs/summary", response_model=LogSummaryResponse)
async def get_logs_summary(
    date_start: str,
    date_finish: str,
    name_entity: str,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    return get_logs_summary_controller(db, date_start, date_finish, name_entity)


@router.get("/logs/detail", response_model=List[LogBase])
async def get_logs_detail(
    date_start: str,
    date_finish: str,
    name_entity: str,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    return get_logs_detail_controller(db, date_start, date_finish, name_entity)


@router.get("/entities")
async def get_available_entities(
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    entities = get_available_entities_controller(db)
    return {"entities": entities}


@router.get("/logs/export-excel")
async def export_logs_to_excel(
    date_start: str,
    date_finish: str,
    name_entity: str,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    """
    Exporta logs a Excel con formato profesional
    
    Args:
        date_start: Fecha de inicio (formato ISO: YYYY-MM-DD)
        date_finish: Fecha de fin (formato ISO: YYYY-MM-DD)
        name_entity: Nombre de la entidad a filtrar
        db: Sesión de base de datos
        current_user: Usuario autenticado
    
    Returns:
        Response: Archivo Excel para descargar
    """
    try:
        # Preparar información del usuario
        user_info = {
            'user_id': current_user.id_user if hasattr(current_user, 'id_user') else None,
            'username': current_user.user if hasattr(current_user, 'user') else 'Usuario'
        }
        
        # Generar Excel
        excel_buffer = export_logs_to_excel_controller(
            db=db,
            date_start=date_start,
            date_finish=date_finish,
            name_entity=name_entity,
            user_info=user_info
        )
        
        # Generar nombre de archivo con fecha actual
        current_date = datetime.now().strftime('%Y-%m-%d')
        filename = f"reporte-{name_entity}-{current_date}.xlsx"
        
        # Retornar archivo Excel como respuesta
        return Response(
            content=excel_buffer.read(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        # El manejo de errores ya está en el controller
        raise


@router.get("/pipes/sector/{id_sector}")
async def report_pipes_sector_(
    id_sector: int,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        report = report_pipes_by_sector(db, id_sector)
        return {
            "success": True,
            "message": "Reporte generado correctamente",
            "data": report
        }
    except Exception as e:
        raise HTTPException(500, f"Error al generar el reporte: {e}")

@router.get("/pipes/interventions/{id_pipes}")
async def report_interventions_pipes_(
    id_pipes: int,
    date_start: str,
    date_finish: str,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        report = report_interventions_by_pipes(db, id_pipes, date_start, date_finish)
        return {
            "success": True,
            "message": "Reporte de intervenciones de tubería generado",
            "data": report
        }
    except Exception as e:
        raise HTTPException(500, f"Error al generar reporte: {e}")

@router.get("/connections/interventions/{id_connection}")
async def report_interventions_connection_(
    id_connection: int,
    date_start: str,
    date_finish: str,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        report = report_interventions_by_connections(db, id_connection, date_start, date_finish)
        return {
            "success": True,
            "message": "Reporte de intervenciones de conexión generado",
            "data": report
        }
    except Exception as e:
        raise HTTPException(500, f"Error al generar el reporte: {e}")

@router.get("/sectors/comparative")
async def report_comparative_sectors(
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        report = report_sector_comparative(db)
        return {
            "success": True,
            "message": "Reporte comparativo entre sectores generado",
            "data": report
        }
    except Exception as e:
        raise HTTPException(500, f"Error al generar el reporte comparativo: {e}")
    
@router.get("/interventions")
async def report_all_interventions(
    date_start: str,
    date_finish: str,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        report = report_interventions(db, date_start, date_finish)
        return {
            "success": True,
            "message": "Reporte general de intervenciones generado",
            "data": report
        }
    except Exception as e:
        raise HTTPException(500, f"Error al generar el reporte: {e}")


@router.get("/interventions/sector/{id_sector}")
async def report_interventions_by_sector_(
    id_sector: int,
    date_start: str,
    date_finish: str,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        report = report_interventions_by_sector(db, date_start, date_finish)
        return {
            "success": True,
            "message": "Reporte de intervenciones por sector generado",
            "data": report
        }
    except Exception as e:
        raise HTTPException(500, f"Error al generar el reporte: {e}")

@router.get("/interventions/frequency")
async def report_intervention_frequency_(
    date_start: str,
    date_finish: str,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        report = report_intervention_frequency(db, date_start, date_finish)
        return {
            "success": True,
            "message": "Reporte de frecuencia de intervenciones generado",
            "data": report
        }
    except Exception as e:
        raise HTTPException(500, f"Error al generar el reporte: {e}")

@router.get("/tanks")
async def report_tanks_(
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    try:
        report = report_tanks(db)
        return {
            "success": True,
            "message": "Reporte de tanques generado correctamente",
            "data": report
        }
    except Exception as e:
        raise HTTPException(500, f"Error al generar el reporte: {e}")