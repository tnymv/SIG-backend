from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime 
from app.db.database import Base
from sqlalchemy.orm import relationship

class TypeEmployee(Base):
    __tablename__ = "type_employees"
    
    id_type_employee = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    state = Column(Boolean, default=True)
    
    employees = relationship("Employee", back_populates="type_employee")