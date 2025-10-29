from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, DECIMAL
from app.models.pipes.pipe_connections import pipe_connections
from sqlalchemy.orm import relationship
from app.db.database import Base
from geoalchemy2 import Geometry
from datetime import datetime

class Connection(Base):
    __tablename__ = "connections"
    id_connection = Column(Integer, primary_key=True, index=True)
    coordenates = Column(Geometry(geometry_type='POINT', srid=4326))
    material = Column(String(50))
    diameter_mn = Column(DECIMAL(10, 2))
    pressure_nominal = Column(String(50))
    connection_type = Column(String(50))
    depth_m  = Column(DECIMAL(5,2))
    installed_date = Column(DateTime)              
    installed_by = Column(String(100))
    description = Column(Text)
    state = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pipes = relationship("Pipes", secondary=pipe_connections, back_populates="connections")
    connection_interventions = relationship("Intervention_entities", back_populates="connection")

