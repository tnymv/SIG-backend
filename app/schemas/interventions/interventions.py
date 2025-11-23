from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InterventionsBase(BaseModel):
    description: str
    status: bool
    start_date: datetime
    end_date: datetime
    photography: list[str] = []

class InterventionsResponse(InterventionsBase):
    id_interventions: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 

class InterventionsCreate(InterventionsBase):
    id_tank: Optional[int] = None
    id_pipes: Optional[int] = None
    id_connection: Optional[int] = None
    
class InterventionsUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    photography: list[str] = []
    updated_at: Optional[datetime] = None