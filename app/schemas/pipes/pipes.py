from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import Field

class PipesBase(BaseModel):
    material: str
    diameter: Decimal = Field(..., max_digits=10, decimal_places=6, gt=0)
    status: bool = True
    size: Decimal = Field(..., max_digits=10, decimal_places=6, gt=0)
    installation_date:datetime
    observations: str
    latitude: float
    longitude: float
    tank_ids: Optional[List[int]] = []

class TankSimple(BaseModel):
    id_tank: int
    name: str

class PipesResponse(BaseModel):
    id_pipes: int
    material: str
    diameter: Decimal = Field(..., max_digits=10, decimal_places=6, gt=0)
    status: bool
    size: Decimal = Field(..., max_digits=10, decimal_places=6, gt=0)
    installation_date:datetime
    latitude: float
    longitude: float
    observations: str
    created_at: datetime
    updated_at: datetime
    tanks: List[TankSimple] = []

    class Config:
        from_attributes = True

class PipesResponseCreate(PipesBase):
    pass

class PipesUpdate(BaseModel):
    material: Optional[str] = None
    diameter: Optional[Decimal] = Field(None, max_digits=10, decimal_places=6, gt=0)
    status: Optional[bool] = None
    size: Optional[Decimal] = Field(None, max_digits=10, decimal_places=6, gt=0)
    installation_date: Optional[datetime] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    observations: Optional[str] = None
    updated_at: datetime = datetime.now()
    tank_ids: Optional[List[int]] = None