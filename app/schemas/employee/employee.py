from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EmployeeBase(BaseModel):
    id_type_employee: int
    first_name: str
    last_name: str
    phone_number: str = None
    state: bool

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    state: Optional[bool] = None
    id_type_employee: Optional[int] = None

class EmployeeResponse(EmployeeBase):
    id_employee: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True