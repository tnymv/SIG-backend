from pydantic import BaseModel
from datetime import datetime

# Campos compartidos por varios schemas
class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    status: int

# Para creación de usuario (entrada)
class EmployeeCreate(EmployeeBase):
    pass  

# Para respuesta al cliente (salida)
class EmployeeResponse(EmployeeBase):
    id_employee: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  
