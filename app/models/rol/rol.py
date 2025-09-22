#models/rol/rol.py
from sqlalchemy import Column, Integer, String,DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from app.db.database import Base

class Rol(Base):
    __tablename__ = "roles"
    id_rol = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1)  # 1: activo, 0: inactivo
    
    # Relación con la tabla Username
    users = relationship("Username", back_populates="rol")