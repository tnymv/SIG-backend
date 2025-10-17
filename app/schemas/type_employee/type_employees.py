from pydantic import BaseModel
from datetime import datetime 
from typing import Optional

class TypeEmployeeBase(BaseModel):
    name: str
    description: Optional[str] = None
    state: bool

class TypeEmployeeResponse(TypeEmployeeBase):
    id_type_employee: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TypeEmployeeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    state: Optional[bool] = None
    updated_at: Optional[datetime] = None
    