from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PermissionsBase(BaseModel):
    name: str
    description: str
    status: bool

class PermissionsResponse(PermissionsBase):
    id_permissions: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PermissionsCreate(PermissionsBase):
    name: str
    description: str
    status: bool

class PermissionsUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None