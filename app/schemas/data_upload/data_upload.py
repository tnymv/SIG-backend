from pydantic import BaseModel
from datetime import datetime, time
from typing import Optional

class Data_uploadBase(BaseModel):
    siaf: str
    municipality: Optional[str] = None
    department: Optional[str] = None
    institutional_classification: int
    report: str
    date: datetime
    hour: time
    seriereport: str
    user: str
    identifier: str
    taxpayer: str
    cologne: str
    cat_service: str
    cannon: float  
    excess: float  
    total: float   
    status: bool = True

class Data_uploadResponse(Data_uploadBase):
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    class Config: 
        from_attributes = True

class Data_uploadCreate(Data_uploadBase):
    pass
    
class Data_uploadUpdate(BaseModel):
    siaf: Optional[str] = None
    municipality: Optional[str] = None
    department: Optional[str] = None
    institutional_classification: Optional[int] = None
    report: Optional[str] = None
    date: Optional[datetime] = None
    hour: Optional[time] = None
    seriereport: Optional[str] = None
    user: Optional[str] = None
    taxpayer: Optional[str] = None
    cologne: Optional[str] = None
    cat_service: Optional[str] = None
    cannon: Optional[float] = None
    excess: Optional[float] = None
    total: Optional[float] = None
    status: Optional[bool] = None
    updated_at: Optional[datetime] = None