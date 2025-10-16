#models/pipes/pipes.py

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from sqlalchemy import Boolean

class Pipes(Base):
    __tablename__ = "pipes"
    id_pipes= Column(Integer, primary_key=True, index=True)
    material= Column(String(50), nullable=False)
    diameter= Column(Integer, nullable=False)
    status=Column(Boolean, default=True)
    size= Column(Integer, index=True, nullable=False)
    installation_date = Column(DateTime, nullable=True)
    coordinates = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    observations=Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    #Relacion con la table
    #pipes = relationship("Pipes", back_populates="connections")
    #pipes = relationship("Pipes", back_populates="interventions")
    #pipes = relationship("Pipes", back_populates="tanks")
    #pipes = relationship("Pipes", back_populates="plumber")