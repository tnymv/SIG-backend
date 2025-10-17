from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, DECIMAL, ForeignKey
from datetime import datetime
from geoalchemy2 import Geometry
from app.db.database import Base
from sqlalchemy.orm import relationship

class Connection(Base):
    __tablename__ = "connections"
    id_connection = Column(Integer, primary_key=True, index=True)
    id_pipe = Column(Integer, ForeignKey("pipes.id_pipes", ondelete="SET NULL"), nullable=False)
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
    
    pipe = relationship("Pipes", back_populates="connections")
