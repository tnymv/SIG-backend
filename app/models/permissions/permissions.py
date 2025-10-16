#models/permissions/permissions.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship

class Permissions(Base):
    __tablename__ = "permissions"

    id_permissions = Column(Integer, primary_key=True, index = True)
    name = Column(String(100), index = True, nullable = False)
    description = Column(String(100), index = True, nullable = False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    #relations
    roles = relationship("Rol",secondary ="rol_permissions", back_populates="permissions")

