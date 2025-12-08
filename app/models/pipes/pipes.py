from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, ForeignKey
from app.models.pipes.pipe_connections import pipe_connections
from app.models.bombs.bombs_pipes import bombs_pipes
from app.models.tanks.tanks_pipes import tank_pipes
from sqlalchemy.orm import relationship
from app.db.database import Base
from geoalchemy2 import Geometry
from datetime import datetime

class Pipes(Base): 
    __tablename__ = "pipes"
    id_pipes= Column(Integer, primary_key=True, index=True)
    material= Column(String(50), nullable=False)
    diameter= Column(Numeric(10, 6), nullable=False)
    active=Column(Boolean, default=True, nullable=False)
    size= Column(Numeric(10, 6), index=True, nullable=False)
    installation_date = Column(DateTime, nullable=True)
    coordinates = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=True)
    distance = Column(Numeric(10, 3), nullable=True)
    sector_id = Column(Integer, ForeignKey("sectors.id_sector"), nullable=True)
    observations=Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    #Relacion con la table
    connections = relationship("Connection", secondary=pipe_connections, back_populates="pipes")
    tanks = relationship("Tank", secondary=tank_pipes, back_populates="pipes")
    pipe_interventions = relationship("Intervention_entities", back_populates="pipe")
    sector = relationship("Sector", back_populates="pipes")
    bombs = relationship("Bombs", secondary=bombs_pipes, back_populates="pipes")