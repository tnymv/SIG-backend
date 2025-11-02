from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.log.logs import LogSummaryResponse, LogBase
from app.schemas.user.user import UserLogin
from app.controllers.auth.auth_controller import get_current_active_user
from app.controllers.Report.report import (
    get_logs_summary_controller,
    get_logs_detail_controller,
    get_available_entities_controller
)

router = APIRouter(prefix='/report', tags=['Reports'])


@router.get("/logs/summary", response_model=LogSummaryResponse)
async def get_logs_summary(
    date_start: str,
    date_finish: str,
    name_entity: str,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    return get_logs_summary_controller(db, date_start, date_finish, name_entity)


@router.get("/logs/detail", response_model=List[LogBase])
async def get_logs_detail(
    date_start: str,
    date_finish: str,
    name_entity: str,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    return get_logs_detail_controller(db, date_start, date_finish, name_entity)


@router.get("/entities")
async def get_available_entities(
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    entities = get_available_entities_controller(db)
    return {"entities": entities}
