from pydantic import BaseModel
from datetime import datetime

# Campos compartidos por varios schemas
class UsernameBase(BaseModel):
    username: str
    password_hash: str
    employee_id: str
    rol_id: int
    status: int

# Para creación de usuario (entrada)
class UsernameCreate(UsernameBase):
    password: str  

# Para respuesta al cliente (salida)
class UsernameResponse(UsernameBase):
    id_username: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  