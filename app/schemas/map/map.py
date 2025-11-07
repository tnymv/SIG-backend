from pydantic import BaseModel, ConfigDict,Field
from typing import List, Optional, Tuple
from decimal import Decimal
from datetime import datetime

class ConnectionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_connection: int
    latitude: float
    longitude: float
    material: str
    pressure_nominal: str
    connection_type: str
    depth_m: Optional[float] = None
    installed_by: str
    state: bool

        
class PipeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_pipes: int
    material: str
    diameter: Decimal = Field(..., max_digits=10, decimal_places=6, gt=0)
    status: bool
    size: Decimal = Field(..., max_digits=10, decimal_places=6, gt=0)
    installation_date: Optional[datetime] = None
    coordinates: List[Tuple[float, float]]
    observations: str
    connections: List[ConnectionSchema] = []

        
class TankSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_tank: int
    name: str
    latitude: float
    longitude: float
    photography: List[str] = []
    state: bool
    pipes: List[PipeSchema] = []