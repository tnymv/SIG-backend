from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship

class Intervention_entities(Base):
    __tablename__ = "intervention_entities"
    id_intervention_entities = Column(Integer, primary_key=True, index = True)
    d_interventions = Column(Integer, ForeignKey("interventions.id_interventions", ondelete="CASCADE"))
    id_tank = Column(Integer, ForeignKey("tanks.id_tank", ondelete="CASCADE"))
    id_pipes = Column(Integer, ForeignKey("pipes.id_pipes", ondelete="CASCADE"))
    id_connection = Column(Integer, ForeignKey("connections.id_connection", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    intervention = relationship("Interventions", back_populates="entities")
    tank = relationship("Tank", back_populates="tank_interventions")
    pipe = relationship("Pipes", back_populates="pipe_interventions")
    connection = relationship("Connection", back_populates="connection_interventions")