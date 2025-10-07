from pydantic import BaseModel
from datetime import datetime 
from typing import Optional, List

class LogBase(BaseModel): 
    user_id: int
    action: str
    entity: Optional[str] = None
    entity_id: Optional[int] = None
    description: str = None
    
    class Config:
        from_attributes = True
        
class ActionSummary(BaseModel):
    action: str
    count: int


class LogSummaryResponse(BaseModel):
    entity: str
    date_range: dict
    total_logs: int
    actions_summary: List[ActionSummary]