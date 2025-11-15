from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.dashboard.dashboard import DashboardStatsResponse
from app.schemas.user.user import UserLogin
from app.controllers.auth.auth_controller import get_current_active_user
from app.controllers.Dashboard.dashboard_stats import get_dashboard_stats
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix='/dashboard', tags=['Dashboard'])

# Caché simple en memoria con timestamp
_cache = {
    "data": None,
    "timestamp": None,
    "ttl": 300  # 5 minutos en segundos
}


def get_cached_stats(db: Session) -> dict:
    """
    Obtiene estadísticas con caché de 5 minutos.
    Si el caché es válido, retorna los datos cacheados.
    Si no, obtiene nuevos datos y actualiza el caché.
    """
    now = datetime.utcnow()
    
    # Verificar si el caché es válido
    if _cache["data"] is not None and _cache["timestamp"] is not None:
        time_elapsed = (now - _cache["timestamp"]).total_seconds()
        if time_elapsed < _cache["ttl"]:
            return _cache["data"]
    
    # Obtener nuevos datos si el caché expiró o no existe
    stats = get_dashboard_stats(db)
    
    # Actualizar caché
    _cache["data"] = stats
    _cache["timestamp"] = now
    
    return stats


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_stats(
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las estadísticas del dashboard en un solo endpoint.
    
    Incluye:
    - Total de usuarios activos
    - Total de empleados activos
    - Total de infraestructura (tanques, tuberías, conexiones)
    - Intervenciones activas y por tipo de entidad
    - Actividad reciente (últimas 10 acciones)
    
    Los datos se cachean por 5 minutos para mejorar el rendimiento.
    """
    try:
        stats = get_cached_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.post("/stats/clear-cache")
async def clear_cache(
    current_user: UserLogin = Depends(get_current_active_user)
):
    """
    Limpia el caché de estadísticas manualmente.
    Útil después de operaciones que modifiquen datos importantes.
    """
    _cache["data"] = None
    _cache["timestamp"] = None
    return {"message": "Caché limpiado exitosamente"}

