from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Campos compartidos por varios schemas
class RolBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: int

# Para creación de usuario (entrada)
class RolCreate(RolBase):
    permission_ids: List[int] = []

# Para respuesta al cliente (salida)
class RolResponse(RolBase):
    id_rol: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  
