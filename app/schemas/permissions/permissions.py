from pydantic import BaseModel
from datetime import datetime

class PermissionsBase(BaseModel):
    name: str
    description: str

class PermissionsCreate(PermissionsBase):
    pass 

class PermissionsResponse(PermissionsBase):
    id_permissions: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True