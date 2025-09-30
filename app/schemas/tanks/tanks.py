from pydantic import BaseModel
from datetime import datetime

class TankBase(BaseModel): 
    name: str
    latitude: float
    longitude: float
    connections: str | None = None
    photos: list[str] = []  # Array de fotos en base64
    photography: str | None = None  # Mantener para compatibilidad
    state: bool
    
class TankResponse(BaseModel):
    id_tank: int
    name: str
    latitude: float
    longitude: float
    connections: str | None = None
    photos: list[str] = []  # Array de fotos
    photography: str | None = None  # Mantener para compatibilidad
    state: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        