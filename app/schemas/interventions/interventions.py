from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class InterventionStatus(str, Enum):
    SIN_INICIAR = "SIN INICIAR"
    EN_CURSO = "EN CURSO"
    FINALIZADO = "FINALIZADO"

class InterventionsBase(BaseModel):
    description: str
    active: bool
    start_date: datetime
    end_date: datetime
    status: InterventionStatus = InterventionStatus.SIN_INICIAR
    photography: list[str] = []

class InterventionsResponse(InterventionsBase):
    id_interventions: int
    created_at: datetime
    updated_at: datetime
    id_tank: Optional[int] = None
    id_pipes: Optional[int] = None
    id_connection: Optional[int] = None

    class Config:
        from_attributes = True 

class InterventionsCreate(InterventionsBase):
    id_tank: Optional[int] = None
    id_pipes: Optional[int] = None
    id_connection: Optional[int] = None
    
class InterventionsUpdate(BaseModel):
    description: Optional[str] = None
    active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[InterventionStatus] = None
    photography: list[str] = []
    updated_at: Optional[datetime] = None
    id_tank: Optional[int] = None
    id_pipes: Optional[int] = None
    id_connection: Optional[int] = None