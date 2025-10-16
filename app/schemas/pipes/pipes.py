from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PipesBase(BaseModel):
    material: str
    diameter: int
    status: bool = True
    size: int
    installation_date:datetime
    observations: str
    latitude: float
    longitude: float

class PipesResponse(BaseModel): 
    pass

class PipesResponse(BaseModel):
    id_pipes: int
    material: str
    diameter: int
    status: bool
    size: int
    installation_date:datetime
    latitude: float
    longitude: float
    observations: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PipesResponseCreate(BaseModel):
    id_pipes: int
    material: str
    diameter: int
    status: bool
    size: int
    installation_date:datetime
    latitude: float
    longitude: float
    observations: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PipesUpdate(BaseModel):
    material: Optional[str] = None
    diameter: Optional[int] = None
    status: Optional[bool] = None
    size: Optional[int] = None
    installation_date: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    observations: Optional[str] = None
    updated_at: datetime = datetime.now()