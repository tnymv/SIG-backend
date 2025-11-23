from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List, Tuple
from decimal import Decimal
from pydantic import Field

class PipesBase(BaseModel):
    material: str
    diameter: Decimal = Field(..., max_digits=10, decimal_places=6, gt=0)
    status: bool = True
    size: Decimal = Field(..., max_digits=10, decimal_places=6, gt=0)
    installation_date:datetime
    observations: Optional[str] = None
    coordinates: List[Tuple[float, float]]
    tank_ids: Optional[List[int]] = []
    start_connection_id: Optional[int] = None
    end_connection_id: Optional[int] = None

    @field_validator('coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        if len(v) != 2:
            raise ValueError('Las coordenadas deben tener exactamente 2 puntos (inicio y fin)')
        return v 

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
    coordinates: List[Tuple[float, float]]
    observations: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tanks: List[TankSimple] = []
    start_connection_id: Optional[int] = None
    end_connection_id: Optional[int] = None

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
    coordinates: Optional[List[Tuple[float, float]]] = None
    observations: Optional[str] = None
    tank_ids: Optional[List[int]] = None
    start_connection_id: Optional[int] = None
    end_connection_id: Optional[int] = None

    @field_validator('coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        if v is not None and len(v) != 2:
            raise ValueError('Las coordenadas deben tener exactamente 2 puntos (inicio y fin)')
        return v