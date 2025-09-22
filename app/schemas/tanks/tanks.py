from pydantic import BaseModel
from datetime import datetime

class TankBase(BaseModel): 
    name: str
    latitude: float
    longitude: float
    connections: str | None = None  # Adjust type as needed
    photography: str 
    state: bool
    
class TankResponse(BaseModel):
    id_tank: int
    latitude: float
    longitude: float
    photography: str 
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        