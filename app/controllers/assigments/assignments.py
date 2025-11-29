from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException
from datetime import datetime
from typing import Optional
from app.models.assignments.assignments import Assignment
from app.models.employee.employee import Employee
from app.models.interventions.interventions import Interventions
from app.schemas.assignments.assignments import AssignmentBase, AssignmentUpdate
from app.schemas.user.user import UserLogin
from app.utils.response import existence_response_dict
from app.utils.logger import create_log


def get_all(db: Session, page: int, limit: int, search: Optional[str] = None):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="La página y el límite deben ser mayores que 0")
    
    offset = (page - 1) * limit
    query = db.query(Assignment)

    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Assignment.status).like(search_term),
                func.lower(func.coalesce(Assignment.notes, "")).like(search_term)
            )
        )

    total = query.count()

    assignments = (
        query.order_by(Assignment.id_assignment.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    if not assignments and not search:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "No hay asignaciones disponibles"),
            headers={"X-Error": "No hay asignaciones disponibles"}
        )

    assignments_list = [
        {
            "id_assignment": a.id_assignment,
            "employee_id": a.employee_id,
            "intervention_id": a.intervention_id,
            "status": a.status,
            "notes": a.notes,
            "active": a.active,
            "assigned_at": a.assigned_at,
            "created_at": a.created_at,
            "updated_at": a.updated_at
        }
        for a in assignments
    ]

    return assignments_list, total


def get_by_id(db: Session, id_assignment: int):
    assignment = db.query(Assignment).filter(Assignment.id_assignment == id_assignment).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "Asignación no encontrada"),
            headers={"X-Error": "Asignación no encontrada"}
        )

    return {
        "id_assignment": assignment.id_assignment,
        "employee_id": assignment.employee_id,
        "intervention_id": assignment.intervention_id,
        "status": assignment.status,
        "notes": assignment.notes,
        "active": assignment.active,
        "assigned_at": assignment.assigned_at,
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at
    }


def create(db: Session, assignment_data: AssignmentBase, user: UserLogin):

    employee = db.query(Employee).filter(
        Employee.id_employee == assignment_data.employee_id,
        Employee.active == True
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )

    intervention = db.query(Interventions).filter(
        Interventions.id_interventions == assignment_data.intervention_id,
        Interventions.active == True
    ).first()

    if not intervention:
        raise HTTPException(
            status_code=404,
            detail="Intervención no encontrada"
        )

    existing = db.query(Assignment).filter(
        Assignment.employee_id == assignment_data.employee_id,
        Assignment.intervention_id == assignment_data.intervention_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="El empleado ya está asignado a esta intervención"
        )

    new_assignment = Assignment(
        employee_id=assignment_data.employee_id,
        intervention_id=assignment_data.intervention_id,
        status=assignment_data.status,
        notes=assignment_data.notes,
        active=True,
        assigned_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_assignment)

    intervention.status = "EN PROCESO"

    db.commit()
    db.refresh(new_assignment)

    create_log(
        db=db,
        user_id=user.id_user,
        action="CREATE",
        entity="Assignment",
        entity_id=new_assignment.id_assignment,
        description=f"Creó una nueva asignación con ID {new_assignment.id_assignment}"
    )

    return new_assignment


def update(db: Session, id_assignment: int, assignment_data: AssignmentUpdate, user: UserLogin):
    assignment = db.query(Assignment).filter(Assignment.id_assignment == id_assignment).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "Asignación no encontrada"),
            headers={"X-Error": "Asignación no encontrada"}
        )

    try:
        updated_data = assignment_data.dict(exclude_unset=True)

        for field, value in updated_data.items():
            setattr(assignment, field, value)

        assignment.updated_at = datetime.utcnow()

        intervention = db.query(Interventions).filter(
            Interventions.id_interventions == assignment.intervention_id
        ).first()

        if intervention and "status" in updated_data:
            if assignment.status == "EN PROCESO":
                intervention.status = "EN PROCESO"
            elif assignment.status == "COMPLETADO":
                intervention.status = "COMPLETADO"
                intervention.end_date = datetime.utcnow()

        db.commit()
        db.refresh(assignment)

        create_log(
            db=db,
            user_id=user.id_user,
            action="UPDATE",
            entity="Assignment",
            entity_id=assignment.id_assignment,
            description=f"Actualizó la asignación con ID {assignment.id_assignment}"
        )

        return assignment

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar la asignación: {str(e)}"
        )


def toggle_state(db: Session, id_assignment: int, user: UserLogin):
    assignment = db.query(Assignment).filter(Assignment.id_assignment == id_assignment).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail=existence_response_dict(False, "Asignación no encontrada"),
            headers={"X-Error": "Asignación no encontrada"}
        )

    assignment.active = not assignment.active
    assignment.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(assignment)

    create_log(
        db=db,
        user_id=user.id_user,
        action="TOGGLE_STATE",
        entity="Assignment",
        entity_id=assignment.id_assignment,
        description=f"Cambió el estado de la asignación con ID {assignment.id_assignment} a {'activo' if assignment.active else 'inactivo'}"
    )

    return assignment