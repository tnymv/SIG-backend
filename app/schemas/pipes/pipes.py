from pydantic import BaseModel
from datetime import datetime

class PipesBase(BaseModel):
    materia: str
    diametro: int
    estado: bool
    fecha_instalacion: datetime

class PipesResponse(BaseModel): 
    pass

class PipesResponse(BaseModel):
    tuberias_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True