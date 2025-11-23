#models/rol/rol.py
from sqlalchemy import Column, Integer, String,DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class Rol(Base):
    __tablename__ = "roles"
    id_rol = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Boolean, default=True)
    
    # Relación con la tabla permisos
    permissions = relationship("Permissions",secondary="rol_permissions", back_populates="roles")
    users = relationship("Username", back_populates="rol") 