from sqlalchemy import Column, Integer, String, DateTime, Boolean, ARRAY
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class Interventions(Base):
    __tablename__ ="interventions"
    id_interventions= Column(Integer, primary_key=True, index=True)
    description = Column(String(200), index=True, nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Boolean, default=True)
    photography = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    entities = relationship("Intervention_entities", back_populates="intervention")
