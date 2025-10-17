from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Campos compartidos por varios schemas
class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    state: bool
    id_type_employee: int  # <-- nuevo campo obligatorio para crear empleado

# Para respuesta al cliente (salida)
class EmployeeResponse(EmployeeBase):
    id_employee: int
    id_type_employee: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    state: Optional[bool] = None
    id_type_employee: Optional[int] = None  # <-- opcional para actualizar
    updated_at: Optional[datetime] = None
