from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship

class Files(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    taxpayer = Column(String(100), index=True, nullable=False) #contribuyente
    cologne = Column(String(200), index=True, nullable=False) #colonia
    cat_service = Column(String(100), index=True, nullable=False)
    canon = Column(Integer, index=True, nullable=False)
    excess = Column(Float, nullable=False)
    total = Column(Integer, index=True, nullable=False)
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)