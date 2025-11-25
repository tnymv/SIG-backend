from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PermissionsBase(BaseModel):
    name: str
    description: str
    active: bool

class PermissionsCreate(PermissionsBase):
    pass

class PermissionsUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None

class PermissionsResponse(PermissionsBase):
    id_permissions: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True