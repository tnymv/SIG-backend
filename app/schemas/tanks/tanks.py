from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class TankBase(BaseModel): 
    name: str
    latitude: float
    longitude: float
    connections: str | None = None
    photography: list[str] = []  # Array de fotos en base64
    state: bool
    
class TankResponse(BaseModel):
    id_tank: int
    name: str
    latitude: float
    longitude: float
    connections: str | None = None
    photography: list[str] = []  # Array de fotos en base64
    state: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
class TankResponseCreate(BaseModel):
    id_tank: int
    name: str
    latitude: float
    longitude: float
    connections: str | None = None
    state: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
class TankUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    connections: Optional[str] = None
    photography: Optional[list[str]] = None  # Array de fotos en base64
    state: Optional[bool] = None
    updated_at: datetime = datetime.now()
    