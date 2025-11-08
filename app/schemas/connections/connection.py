from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import Field

class ConnectionBase(BaseModel):
    latitude: float
    longitude: float
    material: str
    diameter_mn: Decimal = Field(..., max_digits=10, decimal_places=2, gt=0)
    pressure_nominal: str
    connection_type: str 
    depth_m: Decimal = Field(..., max_digits=5, decimal_places=2, gt=0)
    installed_date: datetime
    installed_by: Optional[str] = None
    description: Optional[str] = None
    state: bool = True

class ConnectionCreate(ConnectionBase):
    pipe_ids: Optional[List[int]] = []

class ConnectionUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    material: Optional[str] = None
    diameter_mn: Optional[Decimal] = None
    pressure_nominal: Optional[str] = None
    connection_type: Optional[str] = None 
    depth_m: Optional[Decimal] = None
    installed_date: Optional[datetime] = None
    installed_by: Optional[str] = None
    description: Optional[str] = None
    state: Optional[bool] = None
    pipe_ids: Optional[List[int]] = []

class ConnectionResponse(BaseModel):
    id_connection: int
    latitude: float
    longitude: float
    material: str
    diameter_mn: Decimal = Field(..., max_digits=10, decimal_places=2, gt=0)
    pressure_nominal: str
    connection_type: str
    depth_m: Decimal = Field(..., max_digits=5, decimal_places=2, gt=0)
    installed_date: datetime
    installed_by: Optional[str]
    description: Optional[str]
    state: bool
    created_at: datetime
    updated_at: datetime
    pipes: Optional[List[dict]] = []

    class Config:
        from_attributes = True
