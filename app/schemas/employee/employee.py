from pydantic import BaseModel
from datetime import datetime

# Campos compartidos por varios schemas
class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    state: bool

# Para respuesta al cliente (salida)
class EmployeeResponse(EmployeeBase):
    id_employee: int
    first_name: str
    last_name: str
    phone_number: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  
