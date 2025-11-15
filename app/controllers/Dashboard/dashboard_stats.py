from sqlalchemy.orm import Session
from sqlalchemy import func, case
from fastapi import HTTPException
from app.models.user.user import Username
from app.models.employee.employee import Employee
from app.models.tanks.tanks import Tank
from app.models.pipes.pipes import Pipes
from app.models.connection.connections import Connection
from app.models.interventions.interventions import Interventions
from app.models.intervention_entities.intervention_entities import Intervention_entities
from app.models.log.logs import Logs


def get_dashboard_stats(db: Session):
    """
    Obtiene todas las estadísticas del dashboard en una sola función optimizada.
    Retorna: Diccionario con todas las métricas necesarias para el dashboard
    """
    try:
        # 1. Contar usuarios activos
        active_users = db.query(func.count(Username.id_user)).filter(
            Username.status == True
        ).scalar() or 0

        # 2. Contar empleados activos
        active_employees = db.query(func.count(Employee.id_employee)).filter(
            Employee.state == True
        ).scalar() or 0

        # 3. Contar tanques activos
        active_tanks = db.query(func.count(Tank.id_tank)).filter(
            Tank.state == True
        ).scalar() or 0

        # 4. Contar tuberías activas
        active_pipes = db.query(func.count(Pipes.id_pipes)).filter(
            Pipes.status == True
        ).scalar() or 0

        # 5. Contar conexiones activas
        active_connections = db.query(func.count(Connection.id_connection)).filter(
            Connection.state == True
        ).scalar() or 0

        # 6. Contar intervenciones activas
        active_interventions = db.query(func.count(Interventions.id_interventions)).filter(
            Interventions.status == True
        ).scalar() or 0

        # 7. Contar intervenciones por tipo de entidad
        # Agregamos intervenciones activas por tipo de entidad
        interventions_by_entity = db.query(
            func.sum(case((Intervention_entities.id_tank.isnot(None), 1), else_=0)).label('tanks'),
            func.sum(case((Intervention_entities.id_pipes.isnot(None), 1), else_=0)).label('pipes'),
            func.sum(case((Intervention_entities.id_connection.isnot(None), 1), else_=0)).label('connections')
        ).join(
            Interventions,
            Intervention_entities.d_interventions == Interventions.id_interventions
        ).filter(
            Interventions.status == True
        ).first()

        # Manejar caso donde no hay intervenciones
        tanks_count = int(interventions_by_entity.tanks) if interventions_by_entity.tanks else 0
        pipes_count = int(interventions_by_entity.pipes) if interventions_by_entity.pipes else 0
        connections_count = int(interventions_by_entity.connections) if interventions_by_entity.connections else 0

        # 8. Obtener actividad reciente (últimas 10 acciones)
        recent_logs = db.query(
            Logs.log_id,
            Username.user,
            Logs.action,
            Logs.entity,
            Logs.description,
            Logs.created_at
        ).outerjoin(
            Username,
            Logs.user_id == Username.id_user
        ).order_by(
            Logs.created_at.desc()
        ).limit(10).all()

        # Formatear actividad reciente
        recent_activity = [
            {
                "log_id": log.log_id,
                "user": log.user if log.user else "Sistema",
                "action": log.action,
                "entity": log.entity or "Sistema",
                "description": log.description or f"Acción {log.action} realizada",
                "created_at": log.created_at
            }
            for log in recent_logs
        ]

        # Construir respuesta
        return {
            "users": {
                "active": active_users
            },
            "employees": {
                "active": active_employees
            },
            "infrastructure": {
                "tanks": {"active": active_tanks},
                "pipes": {"active": active_pipes},
                "connections": {"active": active_connections}
            },
            "interventions": {
                "active": active_interventions,
                "by_entity": {
                    "tanks": tanks_count,
                    "pipes": pipes_count,
                    "connections": connections_count
                }
            },
            "recent_activity": recent_activity
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas del dashboard: {str(e)}"
        )

