from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# 🔹 Base con campos comunes
class ConnectionBase(BaseModel):
    latitude: float
    longitude: float
    material: str
    diameter_mn: float
    pressure_nominal: str
    connection_type: str 
    depth_m: float
    installed_date: datetime
    installed_by: Optional[str] = None
    description: Optional[str] = None
    state: bool = True

# 🔹 Crear conexión (puede incluir pipes)
class ConnectionCreate(ConnectionBase):
    pipe_ids: Optional[List[int]] = []

# 🔹 Actualizar conexión (campos opcionales)
class ConnectionUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    material: Optional[str] = None
    diameter_mn: Optional[float] = None
    pressure_nominal: Optional[str] = None
    connection_type: Optional[str] = None 
    depth_m: Optional[float] = None
    installed_date: Optional[datetime] = None
    installed_by: Optional[str] = None
    description: Optional[str] = None
    state: Optional[bool] = None
    pipe_ids: Optional[List[int]] = []
    updated_at: datetime = datetime.now()

# 🔹 Respuesta
class ConnectionResponse(BaseModel):
    id_connection: int
    latitude: float
    longitude: float
    material: str
    diameter_mn: float
    pressure_nominal: str
    connection_type: str
    depth_m: float
    installed_date: datetime
    installed_by: Optional[str]
    description: Optional[str]
    state: bool
    created_at: datetime
    updated_at: datetime
    pipes: Optional[List[dict]] = []

    class Config:
        from_attributes = True
