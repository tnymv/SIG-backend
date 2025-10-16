#models/employee/employee.py

from sqlalchemy import Column, Integer, String,DateTime, Boolean
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship

class Employee(Base):
    __tablename__ = "employees"
    id_employee = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone_number = Column(String(20), nullable=True) 
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    state = Column(Boolean, default=True)
    
    # Relación con la tabla Username
    users = relationship("Username", back_populates="employee")