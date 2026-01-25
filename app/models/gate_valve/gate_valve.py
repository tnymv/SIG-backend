from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.database import Base
from datetime import datetime
from geoalchemy2 import Geometry

class Gate_Valve(Base):
    __tablename__ = "gate_valves"
    id_gate_valve = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    coordinates = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    material = Column(String(50)) 
    diameter = Column(Numeric(10, 6)) 
    photography = Column(ARRAY(String), nullable=True)
    sector_id = Column(Integer, ForeignKey("sectors.id_sector"), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sector = relationship("Sector", back_populates="gate_valves")
    gate_valve_interventions = relationship("Intervention_entities", back_populates="gate_valve")
    pipes = relationship(
        "Pipes", 
        secondary="intervention_entities", 
        back_populates="gate_valves",
        viewonly=True 
    )

   