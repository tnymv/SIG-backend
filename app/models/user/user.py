#models/username/username.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship

class Username(Base):
    __tablename__ = "user"
    
    id_user = Column(Integer, primary_key=True, index=True)
    user = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id_employee"), nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id_rol"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1)  # 1: activo, 0: inactivo
    
    # Relaciones
    employee = relationship("Employee", back_populates="users")
    rol = relationship("Rol", back_populates="users")