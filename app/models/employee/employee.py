#models/employee/employee.py

from sqlalchemy import Column, Integer, String,DateTime
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship

class Employee(Base):
    __tablename__ = "employees"
    id_employee = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), nullable=True) 
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1)  # 1: activo, 0: inactivo
    
    # Relación con la tabla Username
    usernames = relationship("Username", back_populates="employee")