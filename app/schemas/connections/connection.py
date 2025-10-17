from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ConnectionBase(BaseModel):
    id_pipe: int
    latitude: float
    longitude: float
    material: str
    diameter_mn: float
    pressure_nominal: str
    connection_type: str 
    depth_m: float
    installed_date: datetime
    installed_by: str
    description: str
    state: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
class ConnectionResponse(BaseModel):
    id_connection: int
    id_pipe: int
    latitude: float
    longitude: float
    material: str
    diameter_mn: float
    pressure_nominal: str
    connection_type: str
    depth_m: float
    installed_date: datetime
    installed_by: str
    description: str
    state: bool
    created_at: datetime
    updated_at: datetime
    
    class Config: 
        from_attributes = True

class ConnectionCreate(BaseModel):
    id_pipe: int
    latitude: float
    longitude: float
    material: str
    diameter_mn: float
    pressure_nominal: str
    connection_type: str
    depth_m: float
    installed_date: datetime
    description: Optional[str] = None

class ConnectionUpdate(BaseModel):
    id_pipe: Optional[int] = None
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
    updated_at: datetime = datetime.now()