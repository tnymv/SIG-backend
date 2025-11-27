from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class Sector(Base):
    __tablename__ = "sectors"
    id_sector = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True, nullable=False)
    
    # Relación con la tabla de tank, pipes and connections
    tanks = relationship("Tank", back_populates="sector")
    pipes = relationship("Pipes", back_populates="sector")
    connections = relationship("Connection", back_populates="sector")