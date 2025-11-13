from pydantic import BaseModel
from datetime import datetime, time
from typing import Optional

class Data_upload(BaseModel):
    siaf: str
    institutional_classification: int
    report: str
    date: datetime
    hour: time
    seriereport: str
    user: str
    taxpayer: str
    cologne: str
    cat_service: str
    canon: int
    excess: float
    total: int
    status: bool = True

class Data_uploadResponse(Data_upload):
    id: int
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    class Config: 
        from_attributes = True

class Data_uploadCreate(Data_upload):
    pass
    
class Data_uploadUpdate(BaseModel):
    siaf: Optional[str] = None
    institutional_classification: Optional[str] = None
    report: Optional[str] = None
    date: datetime = datetime.now()
    hour: Optional[time] = None
    seriereport: Optional[str] = None
    user: Optional[str] = None
    taxpayer: Optional[str] = None
    cologne: Optional[str] = None
    cat_service: Optional[str] = None
    canon: Optional[int] = None
    excess: Optional[float] = None
    total: Optional[int] = None
    status: Optional[bool] = None
    updated_at: datetime = datetime.now()