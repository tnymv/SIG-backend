from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class TankBase(BaseModel): 
    name: str
    latitude: float
    longitude: float
    connections: str | None = None
    photography: list[str] = []
    state: bool
    
class TankCreate(TankBase):
    pass

class TankUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    connections: Optional[str] = None
    photography: Optional[list[str]] = None
    state: Optional[bool] = None

class TankResponse(TankBase):
    id_tank: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True