from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RecentActivityResponse(BaseModel):
    log_id: int
    user: str
    action: str
    entity: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class InterventionsByEntityResponse(BaseModel):
    tanks: int
    pipes: int
    connections: int


class UsersStatsResponse(BaseModel):
    active: int


class EmployeesStatsResponse(BaseModel):
    active: int


class InfrastructureStatsResponse(BaseModel):
    tanks: dict
    pipes: dict
    connections: dict


class InterventionsStatsResponse(BaseModel):
    active: int
    by_entity: InterventionsByEntityResponse


class DashboardStatsResponse(BaseModel):
    users: UsersStatsResponse
    employees: EmployeesStatsResponse
    infrastructure: InfrastructureStatsResponse
    interventions: InterventionsStatsResponse
    recent_activity: List[RecentActivityResponse]

    class Config:
        from_attributes = True

