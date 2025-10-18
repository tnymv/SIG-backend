from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from pydantic import EmailStr

# Campos compartidos por varios schemas
class UserBase(BaseModel):
    user: str
    password_hash: str
    email: EmailStr
    employee_id: int
    rol_id: int
    status: int

# Para respuesta al cliente (salida)
class UserResponse(BaseModel):
    id_user: int
    user: str
    email: str
    employee_id: int
    rol_id: int
    status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  
        
class UserLogin(BaseModel):
    user: str
    password_hash: str


class UserUpdate(BaseModel):
    user: Optional[str] = None
    password: Optional[str] = None  # Opcional para no cambiarla siempre
    email: Optional[EmailStr] = None
    employee_id: Optional[int] = None
    rol_id: Optional[int] = None
    status: Optional[int] = None