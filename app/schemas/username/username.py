from pydantic import BaseModel
from datetime import datetime

# Campos compartidos por varios schemas
class UsernameBase(BaseModel):
    username: str
    password_hash: str
    employee_id: int
    rol_id: int
    status: int

# Para respuesta al cliente (salida)
class UsernameResponse(UsernameBase):
    id_username: int
    username: str
    status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  
        
class UserLogin(BaseModel):
    username: str
    password_hash: str
    status: int