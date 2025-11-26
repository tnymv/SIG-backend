from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, Time, Float
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class Data_upload(Base):
    __tablename__ = "data_upload"
    # parte del encabezado
    siaf = Column(String(100), index= True, nullable = False)
    municipality = Column(String(200), index=True, nullable=True)  # Municipio
    department = Column(String(200), index=True, nullable=True)  # Departamento
    institutional_classification= Column(Integer, index= True, nullable= False)
    report = Column(String(200), index= True, nullable= False)
    date = Column(DateTime, index= True, nullable= False)
    hour = Column(Time, index=True, nullable= False)
    seriereport = Column (String(100), index=True, nullable= False)
    user = Column(String(100), index= True, nullable=False)
    # infromacion del servicio
    identifier = Column(String(100), primary_key=True, index=True)
    taxpayer= Column(String(100), index=True, nullable=False) #contribuyente
    cologne = Column(String(200), index=True, nullable=False) #colonia
    cat_service = Column(String(250), index=True, nullable=False)
    cannon = Column(Float, index=True, nullable=False)
    excess = Column(Float, index=True, nullable=False)
    total = Column(Float, index=True, nullable=False)
    status = Column(Boolean, index= True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
