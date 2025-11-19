from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List
from app.schemas.map.map import TankSchema
from app.controllers.map.map import get_all_tank_with_pipes_and_connections
from app.controllers.auth.auth_controller import get_current_active_user
from app.schemas.user.user import UserLogin
from app.controllers.map.map import get_interventions_in_range

router = APIRouter(prefix="/map", tags=["Map"])

@router.get("", response_model=List[TankSchema])
def get_all_tanks_complete(db:Session = Depends(get_db),current_user: UserLogin = Depends(get_current_active_user)):
        return get_all_tank_with_pipes_and_connections(db)

@router.get("/map")
def get_interventions_for_map(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_current_active_user)
):
    return get_interventions_in_range(db, start_date, end_date)