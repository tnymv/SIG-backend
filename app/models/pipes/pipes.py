#models/pipes/pipes.py

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship

class Pipes(Base):
    __tablename__ = "pipes"
    tuberias_id= Column(Integer, primary_key=True, index=True)
    materia= Column(String(50), nullable=False)
    diametro= Column(Integer(50), nullable=False)
    estado=Column(bool, nullable=True)
    geom=Column(Integer,(100), nullable=False)
    observaciones=Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    #Relacion con la table
    #pipes = relationship("Pipes", back_populates="connections")
    #pipes = relationship("Pipes", back_populates="interventions")
    #pipes = relationship("Pipes", back_populates="tanks")
    #pipes = relationship("Pipes", back_populates="plumber")