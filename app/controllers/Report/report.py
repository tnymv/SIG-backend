from app.models.log.logs import Logs
from app.models.sector.sector import Sector
from app.models.pipes.pipes import Pipes
from app.models.connection.connections import Connection
from app.models.intervention_entities.intervention_entities import Intervention_entities
from app.models.assignments.assignments import Assignment
from app.models.interventions.interventions import Interventions
from app.models.tanks.tanks import Tank
from app.models.employee.employee import Employee
from app.models.type_employee.type_employees import TypeEmployee
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import func
from app.exports.excel_exporter import ExcelExporter


#Priemros 3 reportes
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

#Reportes del 1 al 3 y el 5
#Reporte 1: Reportes de tuberías por sector
def report_pipes_by_sector(db: Session, id_sector: int):

    sector = db.query(Sector).filter(Sector.id_sector == id_sector).first()

    if not sector:
        raise HTTPException(404, "Sector no encontrado")

    pipes = (
        db.query(Pipes)
        .filter(Pipes.sector_id == id_sector)
        .all()
    )

    result = []

    for pipe in pipes:

        # total de conexiones asociadas
        total_connections = db.query(Connection)\
            .join(Connection.pipes)\
            .filter(Pipes.id_pipes == pipe.id_pipes)\
            .count()

        # total de intervenciones en esta tubería
        total_interventions = db.query(Intervention_entities)\
            .filter(Intervention_entities.id_pipes == pipe.id_pipes)\
            .count()

        result.append({
            "id_pipes": pipe.id_pipes,
            "material": pipe.material,
            "diameter": float(pipe.diameter),
            "size": float(pipe.size),
            "installation_date": pipe.installation_date,
            "distance": float(pipe.distance) if pipe.distance else None,
            "observations": pipe.observations,
            "active": pipe.active,
            "total_connections": total_connections,
            "total_interventions": total_interventions
        })

    return {
        "sector": {
            "id_sector": sector.id_sector,
            "name": sector.name
        },
        "total_pipes": len(result),
        "pipes": result
    }
    
#Reporte 2: Reporte Intervenciones realizadas en tuberías
def report_interventions_by_pipes(db: Session, id_pipes: int, date_start: str, date_finish: str):

    # Convertir fechas
    try:
        start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
        finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))
    except:
        raise HTTPException(400, "Formato de fecha inválido")

    if start_date > finish_date:
        raise HTTPException(400, "La fecha inicial debe ser menor a la fecha final")

    # Obtener tubería
    pipe = db.query(Pipes).filter(Pipes.id_pipes == id_pipes).first()

    if not pipe:
        raise HTTPException(404, "Tubería no encontrada")

    # Obtener entidades relacionadas a esa tubería
    entities = (
        db.query(Intervention_entities)
        .join(Interventions, Interventions.id_interventions == Intervention_entities.d_interventions)
        .filter(Intervention_entities.id_pipes == id_pipes)
        .filter(Interventions.created_at >= start_date)
        .filter(Interventions.created_at <= finish_date)
        .all()
    )

    interventions_list = []

    for entity in entities:
        intervention = entity.intervention

        # obtener asignación + empleado
        assignment = (
            db.query(Assignment)
            .filter(Assignment.intervention_id == intervention.id_interventions)
            .first()
        )

        employee = assignment.employee if assignment else None

        interventions_list.append({
            "id_intervention": intervention.id_interventions,
            "description": intervention.description,
            "status": intervention.status,
            "start_date": intervention.start_date,
            "end_date": intervention.end_date,
            "photography": intervention.photography,

            "assigned_to": f"{employee.first_name} {employee.last_name}" if employee else None,
            "assignment_status": assignment.status if assignment else None,
            "assignment_notes": assignment.notes if assignment else None
        })

    return {
        "pipe": {
            "id_pipes": pipe.id_pipes,
            "material": pipe.material,
            "diameter": float(pipe.diameter),
            "sector_id": pipe.sector_id
        },
        "total_interventions": len(interventions_list),
        "interventions": interventions_list
    }


#Reporte 3: Intervenciones en conexiones
def report_interventions_by_connections(db: Session, id_connection: int, date_start: str, date_finish: str):

    # Convertir fechas
    try:
        start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
        finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))
    except:
        raise HTTPException(400, "Formato de fecha inválido")

    if start_date > finish_date:
        raise HTTPException(400, "La fecha inicial debe ser menor a la fecha final")

    # Obtener conexión
    connection = db.query(Connection).filter(Connection.id_connection == id_connection).first()

    if not connection:
        raise HTTPException(404, "Conexión no encontrada")

    # Obtener entidades relacionadas a esa conexión con filtro por fecha
    entities = (
        db.query(Intervention_entities)
        .join(Interventions, Interventions.id_interventions == Intervention_entities.d_interventions)
        .filter(Intervention_entities.id_connection == id_connection)
        .filter(Interventions.created_at >= start_date)
        .filter(Interventions.created_at <= finish_date)
        .all()
    )

    interventions_list = []

    for entity in entities:
        intervention = entity.intervention

        assignment = (
            db.query(Assignment)
            .filter(Assignment.intervention_id == intervention.id_interventions)
            .first()
        )

        employee = assignment.employee if assignment else None

        interventions_list.append({
            "id_intervention": intervention.id_interventions,
            "description": intervention.description,
            "status": intervention.status,
            "start_date": intervention.start_date,
            "end_date": intervention.end_date,
            "photography": intervention.photography,
            "assigned_to": f"{employee.first_name} {employee.last_name}" if employee else None,
            "assignment_status": assignment.status if assignment else None,
            "assignment_notes": assignment.notes if assignment else None
        })

    return {
        "connection": {
            "id_connection": connection.id_connection,
            "material": connection.material,
            "diameter": float(connection.diameter_mn)
        },
        "total_interventions": len(interventions_list),
        "interventions": interventions_list
    }


#Reporte 5: Reporte comparativo de sectores
def report_sector_comparative(db: Session):

    sectors = db.query(Sector).all()
    if not sectors:
        raise HTTPException(404, "No hay sectores registrados")

    report = []

    for sector in sectors:
        
        pipes = db.query(Pipes).filter(Pipes.sector_id == sector.id_sector).all()
        connections = db.query(Connection).filter(Connection.sector_id == sector.id_sector).all()

        # Intervenciones en tuberías del sector
        pipes_ids = [p.id_pipes for p in pipes]
        connections_ids = [c.id_connection for c in connections]

        interventions_pipes = db.query(Intervention_entities)\
            .filter(Intervention_entities.id_pipes.in_(pipes_ids))\
            .count()

        interventions_connections = db.query(Intervention_entities)\
            .filter(Intervention_entities.id_connection.in_(connections_ids))\
            .count()

        report.append({
            "sector_id": sector.id_sector,
            "sector_name": sector.name,
            "total_pipes": len(pipes),
            "total_connections": len(connections),
            "interventions_pipes": interventions_pipes,
            "interventions_connections": interventions_connections,
            "interventions_total": interventions_pipes + interventions_connections
        })

    return {
        "total_sectors": len(report),
        "results": report
    }

#Reporte del 6 al 8 y 10
#Reporte 6: Reporte Intervenciones
def report_interventions(db: Session, date_start: str, date_finish: str):
    try:
        start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
        finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))

        if start_date > finish_date:
            raise HTTPException(
                status_code=400,
                detail="La fecha inicial debe ser menor a la final"
            )

        interventions = db.query(Interventions).filter(
            Interventions.created_at >= start_date,
            Interventions.created_at <= finish_date
        ).order_by(Interventions.created_at.desc()).all()

        return interventions

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el reporte de intervenciones: {str(e)}"
        )

#Reporte 7: Reporte Intervenciones por sector
def report_interventions_by_sector(db: Session, date_start: str, date_finish: str):
    try:
        start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
        finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))

        # Tuberías
        pipes_query = (
            db.query(Sector.name, func.count(Intervention_entities.id_intervention_entities))
            .join(Pipes, Pipes.id_pipes == Intervention_entities.id_pipes)
            .join(Sector, Sector.id_sector == Pipes.sector_id)
            .filter(
                Intervention_entities.created_at >= start_date,
                Intervention_entities.created_at <= finish_date
            )
            .group_by(Sector.name)
        )

        # Tanques
        tanks_query = (
            db.query(Sector.name, func.count(Intervention_entities.id_intervention_entities))
            .join(Tank, Tank.id_tank == Intervention_entities.id_tank)
            .join(Sector, Sector.id_sector == Tank.sector_id)
            .filter(
                Intervention_entities.created_at >= start_date,
                Intervention_entities.created_at <= finish_date
            )
            .group_by(Sector.name)
        )

        # Conexiones
        conn_query = (
            db.query(Sector.name, func.count(Intervention_entities.id_intervention_entities))
            .join(Connection, Connection.id_connection == Intervention_entities.id_connection)
            .join(Sector, Sector.id_sector == Connection.sector_id)
            .filter(
                Intervention_entities.created_at >= start_date,
                Intervention_entities.created_at <= finish_date
            )
            .group_by(Sector.name)
        )

        # unir resultados
        results = {}

        for name, count in pipes_query:
            results[name] = results.get(name, 0) + count

        for name, count in tanks_query:
            results[name] = results.get(name, 0) + count

        for name, count in conn_query:
            results[name] = results.get(name, 0) + count

        # ordenar de mayor a menor como indica el documento
        ordered = sorted(
            [{"sector": k, "total_intervenciones": v} for k, v in results.items()],
            key=lambda x: x["total_intervenciones"],
            reverse=True
        )

        return ordered

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar intervenciones por sector: {str(e)}"
        )

#Reporte 8: Frecuencia 
def report_intervention_frequency(db: Session, date_start: str, date_finish: str):
    try:
        # Convertir fechas ISO con soporte para Z
        start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
        finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))

        # Validación
        if start_date > finish_date:
            raise HTTPException(
                status_code=400,
                detail="La fecha inicial no puede ser mayor que la fecha final"
            )

        # Consulta
        freq = (
            db.query(
                Interventions.description,
                func.count(Interventions.id_interventions).label("count")
            )
            .filter(
                Interventions.created_at >= start_date,
                Interventions.created_at <= finish_date
            )
            .group_by(Interventions.description)
            .order_by(func.count(Interventions.id_interventions).desc())
            .all()
        )

        return [
            {"description": desc, "cantidad": count}
            for desc, count in freq
        ]

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido. Use YYYY-MM-DD o ISO 8601"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en el reporte de frecuencia: {str(e)}"
        )

#Reporte 10: Reporte tanques
def report_tanks(db: Session):
    try:
        tanks = db.query(Tank).all()

        result = []

        for tank in tanks:
            result.append({
                "id_tank": tank.id_tank,
                "name": tank.name,
                "coordinates": db.scalar(func.ST_AsText(tank.coordinates)) if tank.coordinates else None,
                "photos": tank.photography,
                "created_at": tank.created_at
            })

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el reporte de tanques: {str(e)}"
        )

#Reporte 11: Reporte de estado por tanque
def report_tank_status(db: Session):
    try:
        tanks = db.query(Tank).all()
        result = []

        for tank in tanks:
            # Total de intervenciones asociadas
            total_interventions = (
                db.query(Intervention_entities)
                .filter(Intervention_entities.id_tank == tank.id_tank)
                .count()
            )

            # Última intervención
            last_intervention = (
                db.query(Intervention_entities)
                .filter(Intervention_entities.id_tank == tank.id_tank)
                .join(Interventions, Interventions.id_interventions == Intervention_entities.d_interventions)
                .order_by(Interventions.created_at.desc())
                .first()
            )

            result.append({
                "id_tank": tank.id_tank,
                "name": tank.name,
                "state": "ACTIVO" if tank.active else "INACTIVO",
                "coordinates": db.scalar(func.ST_AsText(tank.coordinates)) if tank.coordinates else None,
                "photos": tank.photography,
                "created_at": tank.created_at,
                "total_interventions": total_interventions,
                "last_intervention": last_intervention.intervention.description if last_intervention else None
            })

        return result

    except Exception as e:
        raise HTTPException(500, f"Error al generar reporte de estado de tanques: {str(e)}")

#Reporte 12: Reporte de desvios
def report_deviations(db: Session):
    try:
        connections = db.query(Connection).all()
        result = []

        for conn in connections:
            total_interventions = (
                db.query(Intervention_entities)
                .filter(Intervention_entities.id_connection == conn.id_connection)
                .count()
            )

            result.append({
                "id_connection": conn.id_connection,
                "sector": conn.sector.name if conn.sector else None,
                "material": conn.material,
                "type": conn.connection_type,
                "installed_date": conn.installed_date,
                "coordinates": db.scalar(func.ST_AsText(conn.coordenates)) if conn.coordenates else None,
                "active": conn.active,
                "total_interventions": total_interventions
            })

        return result

    except Exception as e:
        raise HTTPException(500, f"Error al generar reporte de desvíos: {str(e)}")

#Reporte 14: Reporte de trabajos asignados
# Reporte 14: Trabajos asignados (con rango de fechas)
def report_assigned_jobs(db: Session, date_start: str, date_finish: str):
    try:
        start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
        finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))

        assignments = (
            db.query(Assignment)
            .filter(
                Assignment.assigned_at >= start_date,
                Assignment.assigned_at <= finish_date
            )
            .order_by(Assignment.assigned_at.desc())
            .all()
        )

        result = []
        for a in assignments:
            result.append({
                "id_assignment": a.id_assignment,
                "assigned_at": a.assigned_at,
                "status": a.status,
                "notes": a.notes,

                "employee": {
                    "id": a.employee.id_employee,
                    "name": f"{a.employee.first_name} {a.employee.last_name}"
                },

                "intervention": {
                    "id": a.intervention.id_interventions,
                    "description": a.intervention.description,
                    "status": a.intervention.status
                }
            })

        return {
            "total_assignments": len(result),
            "assignments": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en el reporte de trabajos asignados: {str(e)}"
        )


#Reporte 15: Trabajo asignado por estado
def report_assigned_jobs_by_status(db: Session, date_start: str, date_finish: str):
    try:
        start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
        finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))

        assignments = (
            db.query(Assignment)
            .filter(
                Assignment.assigned_at >= start_date,
                Assignment.assigned_at <= finish_date
            )
            .order_by(Assignment.status, Assignment.assigned_at.desc())
            .all()
        )

        # contador por estado
        status_count = {}
        for a in assignments:
            status_count[a.status] = status_count.get(a.status, 0) + 1

        # detalle
        results = []
        for a in assignments:
            results.append({
                "id_assignment": a.id_assignment,
                "status": a.status,
                "assigned_at": a.assigned_at,
                "notes": a.notes,

                "employee": {
                    "id": a.employee.id_employee,
                    "name": f"{a.employee.first_name} {a.employee.last_name}"
                },

                "intervention": {
                    "id": a.intervention.id_interventions,
                    "description": a.intervention.description
                }
            })

        return {
            "summary": status_count,
            "total_assignments": len(results),
            "assignments": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en el reporte de trabajos por estado: {str(e)}"
        )

#Reporte 16: Reporte de fontanero
def report_plumber(db: Session, employee_id: int, date_start: str, date_finish: str):
    try:
        start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
        finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))

        employee = db.query(Employee).filter(Employee.id_employee == employee_id).first()
        if not employee:
            raise HTTPException(404, "Empleado no encontrado")

        if employee.type_employee.name.lower() != "fontanero":
            raise HTTPException(400, "El empleado no es fontanero")

        assignments = (
            db.query(Assignment)
            .filter(
                Assignment.employee_id == employee_id,
                Assignment.assigned_at >= start_date,
                Assignment.assigned_at <= finish_date
            )
            .all()
        )

        return {
            "id_employee": employee.id_employee,
            "name": f"{employee.first_name} {employee.last_name}",
            "total_trabajos": len(assignments),
            "asignado": sum(a.status == "ASIGNADO" for a in assignments),
            "en_proceso": sum(a.status == "EN PROCESO" for a in assignments),
            "completado": sum(a.status == "COMPLETADO" for a in assignments),
        }

    except Exception as e:
        raise HTTPException(500, f"Error reporte fontanero: {e}")



#Reporte 17: Reporte de fontaneros más activos
def report_top_plumbers(db: Session, date_start: str, date_finish: str):

    start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
    finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))

    plumbers = (
        db.query(Employee)
        .join(TypeEmployee, TypeEmployee.id_type_employee == Employee.id_type_employee)
        .filter(TypeEmployee.name == "Fontanero")
        .all()
    )

    results = []

    for emp in plumbers:
        count = (
            db.query(Assignment)
            .filter(
                Assignment.employee_id == emp.id_employee,
                Assignment.assigned_at >= start_date,
                Assignment.assigned_at <= finish_date
            )
            .count()
        )
        results.append({
            "employee": f"{emp.first_name} {emp.last_name}",
            "id_employee": emp.id_employee,
            "total_trabajos": count
        })

    return sorted(results, key=lambda x: x["total_trabajos"], reverse=True)


#Reporte 18: Reporte de operadores
def report_operator(db: Session, employee_id: int, date_start: str, date_finish: str):

    start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
    finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))

    employee = db.query(Employee).filter(Employee.id_employee == employee_id).first()
    if not employee:
        raise HTTPException(404, "Empleado no encontrado")

    if employee.type_employee.name.lower() != "operador":
        raise HTTPException(400, "El empleado no es operador")

    assignments = (
        db.query(Assignment)
        .filter(
            Assignment.employee_id == employee_id,
            Assignment.assigned_at >= start_date,
            Assignment.assigned_at <= finish_date
        )
        .all()
    )

    return {
        "id_employee": employee.id_employee,
        "name": f"{employee.first_name} {employee.last_name}",
        "total_trabajos": len(assignments),
        "asignado": sum(a.status == "ASIGNADO" for a in assignments),
        "en_proceso": sum(a.status == "EN PROCESO" for a in assignments),
        "completado": sum(a.status == "COMPLETADO" for a in assignments),
    }


#Reporte 19: Reporte de operadores más activos
def report_top_operators(db: Session, date_start: str, date_finish: str):
    start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
    finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))

    operators = (
        db.query(Employee)
        .join(TypeEmployee, TypeEmployee.id_type_employee == Employee.id_type_employee)
        .filter(TypeEmployee.name == "Operador")
        .all()
    )

    results = []

    for emp in operators:
        count = (
            db.query(Assignment)
            .filter(
                Assignment.employee_id == emp.id_employee,
                Assignment.assigned_at >= start_date,
                Assignment.assigned_at <= finish_date
            )
            .count()
        )
        results.append({
            "employee": f"{emp.first_name} {emp.last_name}",
            "id_employee": emp.id_employee,
            "total_trabajos": count
        })

    return sorted(results, key=lambda x: x["total_trabajos"], reverse=True)


#Reporte 20: Reporte de Lectores
def report_readers(db: Session, date_start: str, date_finish: str):
    start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
    finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))

    readers = (
        db.query(Employee)
        .join(TypeEmployee, TypeEmployee.id_type_employee == Employee.id_type_employee)
        .filter(TypeEmployee.name == "Lector")
        .all()
    )

    result = []

    for emp in readers:
        actividad = (
            db.query(Assignment)
            .filter(
                Assignment.employee_id == emp.id_employee,
                Assignment.assigned_at >= start_date,
                Assignment.assigned_at <= finish_date
            )
            .count()
        )
        result.append({
            "id_employee": emp.id_employee,
            "nombre": f"{emp.first_name} {emp.last_name}",
            "actividad": actividad
        })

    return result

#Repote 21: Reporte de Lectores más activos
def report_top_readers(db: Session, date_start: str, date_finish: str):

    start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
    finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))

    readers = (
        db.query(Employee)
        .join(TypeEmployee)
        .filter(TypeEmployee.name == "Lector")
        .all()
    )

    results = []

    for emp in readers:
        count = (
            db.query(Assignment)
            .filter(
                Assignment.employee_id == emp.id_employee,
                Assignment.assigned_at >= start_date,
                Assignment.assigned_at <= finish_date
            )
            .count()
        )

        results.append({
            "employee": f"{emp.first_name} {emp.last_name}",
            "id_employee": emp.id_employee,
            "total_trabajos": count
        })

    return sorted(results, key=lambda x: x["total_trabajos"], reverse=True)


#Reporte 22: Reporte de encargados de limpieza
def report_encargados_limpieza(db: Session):
    try:
        tipo = (
            db.query(TypeEmployee)
            .filter(TypeEmployee.name == "Encargado de limpieza")
            .first()
        )

        if not tipo:
            raise HTTPException(404, "No existe el tipo 'Encargado de limpieza'")

        empleados = (
            db.query(Employee)
            .filter(Employee.id_type_employee == tipo.id_type_employee)
            .all()
        )

        return [
            {
                "id_employee": emp.id_employee,
                "nombre": f"{emp.first_name} {emp.last_name}",
                "telefono": emp.phone_number,
                "activo": emp.active
            }
            for emp in empleados
        ]

    except Exception as e:
        raise HTTPException(500, f"Error en reporte encargados de limpieza: {e}")

#Reporte 23: Reporte de encargados de limpieza más activos
def report_top_cleaners(db: Session, date_start: str, date_finish: str):
    start_date = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
    finish_date = datetime.fromisoformat(date_finish.replace("Z", "+00:00"))

    cleaners = (
        db.query(Employee)
        .join(TypeEmployee)
        .filter(TypeEmployee.name == "Encargado de limpieza")
        .all()
    )

    results = []

    for emp in cleaners:
        count = (
            db.query(Assignment)
            .filter(
                Assignment.employee_id == emp.id_employee,
                Assignment.assigned_at >= start_date,
                Assignment.assigned_at <= finish_date
            )
            .count()
        )

        results.append({
            "id_employee": emp.id_employee,
            "nombre": f"{emp.first_name} {emp.last_name}",
            "actividad": count
        })

    return sorted(results, key=lambda x: x["actividad"], reverse=True)
