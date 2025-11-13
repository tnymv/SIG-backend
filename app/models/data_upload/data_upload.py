from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, Time
from app.models.data_upload.data_upload import data_upload
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class Data_upload(Base):
    __tablename__ = "data_upload"
    id_data_upload = Column(Integer, primary_key=True, index=True)
    # parte del encabezado
    siaf = Column(String(100), index= True, nullable = False)
    institutional_classification= Column(Integer, index= True, nullable= False)
    report = Column(String(200), index= True, nullable= False)
    date = Column(DateTime, index= True, nullable= False)
    hour = Column(Time, index=True, nullable= False)
    seriereport = Column (String(100), index=True, nullable= False)
    user = Column(String(100), index= True, nullable=False)
    # infromacion del servicio
    identifier = Column(String(100), index= True, nullable= False)
    taxpayer= Column(String(100), index=True, nullable=False) #contribuyente
    cologne = Column(String(200), index=True, nullable=False) #colonia
    cat_service = Column(String(250), index=True, nullable=False)
    cannon =  Column(Integer, index=True, nullable=False)
    excess = Column(Integer, index=True, nullable=False)
    total = Column(Integer, index=True, nullable=False)
