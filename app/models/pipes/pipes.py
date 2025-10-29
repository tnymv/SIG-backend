from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.models.pipes.pipe_connections import pipe_connections
from app.models.tanks.tanks_pipes import tank_pipes
from sqlalchemy.orm import relationship
from app.db.database import Base
from geoalchemy2 import Geometry
from datetime import datetime

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
    connections = relationship("Connection", secondary=pipe_connections, back_populates="pipes")
    tanks = relationship("Tank", secondary=tank_pipes, back_populates="pipes")
    pipe_interventions = relationship("Intervention_entities", back_populates="pipe")