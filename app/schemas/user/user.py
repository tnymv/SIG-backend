from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from pydantic import EmailStr

# Campos compartidos por varios schemas
class UserBase(BaseModel):
    user: str
    password_hash: str
    email: EmailStr
    employee_id: int
    rol_id: int
    active: bool

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    user: Optional[str] = None
    password: Optional[str] = None  # Opcional para no cambiarla siempre
    email: Optional[EmailStr] = None
    employee_id: Optional[int] = None
    rol_id: Optional[int] = None
    active: Optional[bool] = None

class PermissionInfo(BaseModel):
    id_permissions: int
    name: str
    description: str
    active: bool

    class Config:
        from_attributes = True

# Schema para información del rol
class RolInfo(BaseModel):
    id_rol: int
    name: str
    description: Optional[str]
    active: bool

    class Config:
        from_attributes = True

# Para respuesta al cliente (salida)
class UserResponse(UserBase):
    id_user: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  


class UserResponseWithPermissions(UserResponse):
    rol: Optional[RolInfo] = None
    permissions: List[PermissionInfo] = []

    class Config:
        from_attributes = True
        
class UserLogin(BaseModel):
    user: str
    password_hash: str