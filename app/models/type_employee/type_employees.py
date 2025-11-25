from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime 

class TypeEmployee(Base):
    __tablename__ = "type_employees"
    
    id_type_employee = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True, nullable=False)
    
    employees = relationship("Employee", back_populates="type_employee")