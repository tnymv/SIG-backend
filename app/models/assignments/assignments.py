from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime 

class Assignment(Base):
    __tablename__ = "assignments"
    id_assignment = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id_employee"), nullable=False)
    intervention_id = Column(Integer, ForeignKey("interventions.id_interventions"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="ASIGNADO")  # asignado, en proceso, completado
    notes = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    employee = relationship("Employee", back_populates="assignments")
    intervention = relationship("Interventions", back_populates="assignments")