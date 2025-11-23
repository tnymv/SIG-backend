from sqlalchemy import Column, Integer, ForeignKey, DateTime
from app.db.database import Base
from datetime import datetime

class Rol_permissions(Base):
    __tablename__ = "rol_permissions"
    id_rol_permissions =Column(Integer, primary_key=True, index = True)
    id_permissions = Column(Integer, ForeignKey("permissions.id_permissions", ondelete="CASCADE"))  
    id_rol = Column(Integer, ForeignKey("roles.id_rol", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)