from pydantic import BaseModel
from datetime import datetime 
from typing import Optional 

class SectorBase(BaseModel):
    name: str
    description: str
    active: bool 
    
class SectorCreate(SectorBase):
    pass

class SectorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    
class SectorResponse(SectorBase):
    id_sector: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True