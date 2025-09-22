from pydantic import BaseModel
from datetime import datetime

# Campos compartidos por varios schemas
class UserBase(BaseModel):
    user: str
    password_hash: str
    employee_id: int
    rol_id: int
    status: int

# Para respuesta al cliente (salida)
class UserResponse(UserBase):
    id_user: int
    user: str
    status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  
        
class UserLogin(BaseModel):
    user: str
    password_hash: str
