from pydantic import BaseModel
from datetime import datetime

# Campos compartidos por varios schemas
class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    departament: str
    status: int

# Para creación de usuario (entrada)
class EmployeeCreate(EmployeeBase):
    pass  # Si necesitaras password, aquí lo agregas

# Para respuesta al cliente (salida)
class EmployeeOut(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Permite convertir desde un modelo SQLAlchemy
