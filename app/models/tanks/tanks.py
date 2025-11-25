from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.models.tanks.tanks_pipes import tank_pipes
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship 
from app.db.database import Base
from geoalchemy2 import Geometry
from datetime import datetime

class Tank(Base):
    __tablename__ = "tanks"
    
    id_tank = Column(Integer, primary_key = True, index = True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    coordinates = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    connections = Column(String)  # Pendiente definir el tipo de dato adecuado, asi que esto puede cambiar con el tiempo
    photography = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True, nullable=False)
    
    pipes = relationship("Pipes", secondary=tank_pipes, back_populates="tanks")
    tank_interventions = relationship("Intervention_entities", back_populates="tank")