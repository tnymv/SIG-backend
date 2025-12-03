from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BombsBase(BaseModel):
    name: str 
    latitude: float
    longitude: float
    connections: str | None = None
    photography: list[str] = []
    sector_id: int
    active: bool

class BombsCreate(BombsBase):
    pass

class BombsUpdate(BombsBase):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    connections: Optional[str] = None
    photography: Optional[list[str]] = None
    sector_id: Optional[int] = None
    active: Optional[bool] = None

class BombsResponse(BombsBase):
    id_bombs: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True