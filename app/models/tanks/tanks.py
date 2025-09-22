#model/tanks/tanks.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from datetime import datetime
from app.db.database import Base
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship 

class Tank(Base):
    __tablename__ = "tanks"
    
    id_tank = Column(Integer, primary_key = True, index = True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    coordinates = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    connections = Column(String)  # Pendiente definir el tipo de dato adecuado, asi que esto puede cambiar con el tiempo
    photography = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    state = Column(Boolean, default=True)  # True: activo, False: inactivo
    