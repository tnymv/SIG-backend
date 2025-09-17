from pydantic import BaseModel
from datetime import datetime

# Campos compartidos por varios schemas
class RolBase(BaseModel):
    name: str
    description: str
    status: int

# Para creación de usuario (entrada)
class RolCreate(RolBase):
    pass  

# Para respuesta al cliente (salida)
class RolResponse(RolBase):
    id_rol: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  
