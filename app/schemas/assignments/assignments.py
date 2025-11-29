from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class AssignmentBase(BaseModel):
    employee_id: int = Field(..., description="ID del empleado asignado")
    intervention_id: int = Field(..., description="ID de la intervención asignada")
    status: str = Field(default="ASIGNADO", description="ASIGNADO | EN PROCESO | COMPLETADO")
    notes: Optional[str] = Field(default=None, description="Notas adicionales sobre la asignación")

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    active: Optional[bool] = None

class AssignmentResponse(AssignmentBase):
    id_assignment: int
    assigned_at: datetime
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
