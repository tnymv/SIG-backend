from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Numeric, Time, Float
from sqlalchemy.orm import relationship
from app.models.bombs.bombs_pipes import bombs_pipes
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.database import Base
from datetime import datetime
from geoalchemy2 import Geometry

class Bombs(Base):
    __tablename__ = "bombs"
    id_bombs = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    coordinates = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    connections = Column(String)  # Pendiente definir el tipo de dato adecuado, asi que esto puede cambiar con el tiempo
    photography = Column(ARRAY(String), nullable=True)
    sector_id = Column(Integer, ForeignKey("sectors.id_sector"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True, nullable=False)

    pipes = relationship("Pipes", secondary=bombs_pipes, back_populates="bombs")
    sector = relationship("Sector", back_populates="bombs")
    bombs_interventions = relationship(
        "Intervention_entities", 
        back_populates="bombs",
        foreign_keys="[Intervention_entities.id_bombs]"
    )

    