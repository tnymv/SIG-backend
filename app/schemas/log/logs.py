from pydantic import BaseModel
from datetime import datetime 
from typing import Optional

class LogBase(BaseModel): 
    user_id: int
    action: str
    entity: Optional[str] = None
    entity_id: Optional[int] = None
    description: str = None
    
    class Config:
        from_attributes = True