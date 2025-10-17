#model/tanks/tanks.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.db.database import Base
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship 
from sqlalchemy.dialects.postgresql import ARRAY
from app.models.tanks.tanks_pipes import tank_pipes

class Tank(Base):
    __tablename__ = "tanks"
    
    id_tank = Column(Integer, primary_key = True, index = True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    coordinates = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    connections = Column(String)  # Pendiente definir el tipo de dato adecuado, asi que esto puede cambiar con el tiempo
    photography = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    state = Column(Boolean, default=True)
    
    pipes = relationship("Pipes", secondary=tank_pipes, back_populates="tanks")