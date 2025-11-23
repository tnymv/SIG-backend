from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FilesBase(BaseModel):
    taxpayer: str
    cologne: str
    cat_service: str
    canon: int
    excess: float
    total: int
    status: bool = True

class FilesResponse(FilesBase):
    id: int
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    class Config: 
        from_attributes = True

class FilesCreate(FilesBase):
    pass
    
class FilesUpdate(BaseModel):
    taxpayer: Optional[str] = None
    cologne: Optional[str] = None
    cat_service: Optional[str] = None
    canon: Optional[int] = None
    excess: Optional[float] = None
    total: Optional[int] = None
    status: Optional[bool] = None
    updated_at: datetime = datetime.now()