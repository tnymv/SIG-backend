from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from pydantic import Field
from decimal import Decimal

class Gate_valveBase(BaseModel): 
    name: str
    latitude: float
    longitude: float
    connections: str | None = None
    material: str
    diameter: Decimal = Field(..., max_digits=10, decimal_places=2, gt=0)
    photography: list[str] = []
    sector_id: int
    active: bool
    
class Gate_valveCreate(Gate_valveBase):
    pass

class Gate_valveUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    connections: Optional[str] = None
    material: Optional[str] = None
    diameter: Optional[Decimal] = None 
    photography: Optional[list[str]] = None
    sector_id: Optional[int] = None
    active: Optional[bool] = None

class Gate_valveResponse(Gate_valveBase):
    id_gate_valve: int
    name: str
    material: str
    diameter: Decimal = Field(..., max_digits=10, decimal_places=2, gt=0)
    photography: Optional[list[str]] = None
    sector_id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True