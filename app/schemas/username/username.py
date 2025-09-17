from pydantic import BaseModel
from datetime import datetime

# Campos compartidos por varios schemas
class EmployeeBase(BaseModel):
    username: str
    password_hash: str
    employee_id: str
    rol_id: int
    status: int

# Para creación de usuario (entrada)
class EmployeeCreate(EmployeeBase):
    password: str  

# Para respuesta al cliente (salida)
class EmployeeOut(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Permite convertir desde un modelo SQLAlchemy
