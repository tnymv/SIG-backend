#models/log/logs.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime 
from app.db.database import Base
from sqlalchemy.orm import relationship

class Logs(Base): 
    __tablename__ = "logs"
    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id_user"), nullable=False)
    action = Column(String(50), nullable=False)
    entity = Column(String(50))
    entity_id = Column(Integer)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("Username", back_populates="logs")
