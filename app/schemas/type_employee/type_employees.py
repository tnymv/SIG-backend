from pydantic import BaseModel
from datetime import datetime 
from typing import Optional

class TypeEmployeeBase(BaseModel):
    name: str
    description: str
    active: bool
    
class TypeEmployeeCreate(TypeEmployeeBase): 
    pass

class TypeEmployeeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None

class TypeEmployeeResponse(TypeEmployeeBase):
    id_type_employee: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True