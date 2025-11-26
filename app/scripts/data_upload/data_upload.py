import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime
import sys
import os

# ruta para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from app.schemas.data_upload.data_upload import Data_uploadCreate

class ExcelProcessor:
    def __init__(self, current_user=None):
        self.current_user = current_user
        self.valid_data = []
        self.errors = []
    
    def process_excel_content(self, file_content: bytes) -> Tuple[List[Data_uploadCreate], List[str]]:
        """Procesa contenido de Excel y retorna datos para la BD"""
        try:
            # Leer Excel saltando encabezados
            df = pd.read_excel(file_content, skiprows=8)
            print(f" Excel procesado: {len(df)} filas encontradas")
            print(f"Columnas detectadas: {list(df.columns)}")
            
            # Procesar cada fila
            for index, row in df.iterrows():
                row_errors = self._validate_row(row, index + 9)
                
                if not row_errors:
                    # Preparar datos para Data_uploadCreate
                    data_dict = {
                        # Encabezado fijo
                        "siaf": "SERVICIOSGL",
                        "institutional_classification": 12100924,
                        "report": "Morosidad Servicio De Agua", 
                        "date": datetime.now(),
                        "hour": datetime.now().time(),
                        "seriereport": "R00809001.rpt",
                        "user": self._get_cell_value(row, 'USUARIO', "SYSTEM"),
                        "status": True,
                        # Datos del Excel
                        "identifier": self._get_cell_value(row, 'IDENTIFICADOR', f"AUTO-{index+9}"),
                        "taxpayer": self._get_cell_value(row, 'CONTRIBUYENTE'),
                        "cologne": self._get_cell_value(row, 'COLONIA'),
                        "cat_service": self._get_cell_value(row, 'CAT_SERVICIO', ""),
                        "cannon": self._get_numeric_value(row, 'CANON'),
                        "excess": self._get_numeric_value(row, 'EXCESO'),
                        "total": self._get_numeric_value(row, 'TOTAL')
                    }
                    
                    # Crear objeto Data_uploadCreate
                    self.valid_data.append(Data_uploadCreate(**data_dict))
                    print(f"Fila {index + 9} procesada: {data_dict['taxpayer']}")
                    
                else:
                    self.errors.extend(row_errors)
                    print(f"Errores en fila {index + 9}: {row_errors}")
            
            print(f" Procesamiento completado: {len(self.valid_data)} válidos, {len(self.errors)} errores")
            return self.valid_data, self.errors
            
        except Exception as e:
            error_msg = f"Error al procesar archivo Excel: {str(e)}"
            self.errors.append(error_msg)
            print(f"{error_msg}")
            return [], self.errors
    
    def _validate_row(self, row: pd.Series, row_num: int) -> List[str]:
        """Valida una fila individual del Excel"""
        errors = []
        
        # Validar campos requeridos
        taxpayer = self._get_cell_value(row, 'CONTRIBUYENTE')
        if not taxpayer:
            errors.append("CONTRIBUYENTE es requerido")
        
        cologne = self._get_cell_value(row, 'COLONIA')
        if not cologne:
            errors.append("COLONIA es requerido")
        
        # Validar números
        cannon = self._get_numeric_value(row, 'CANON')
        if cannon < 0:
            errors.append("CANON no puede ser negativo")
        
        excess = self._get_numeric_value(row, 'EXCESO')
        if excess < 0:
            errors.append("EXCESO no puede ser negativo")
        
        total = self._get_numeric_value(row, 'TOTAL')
        if total < 0:
            errors.append("TOTAL no puede ser negativo")
        
        return errors
    
    def _get_cell_value(self, row: pd.Series, column_name: str, default: str = "") -> str:
        """Obtiene valor de celda como string limpio"""
        value = row.get(column_name, default)
        if pd.isna(value) or value is None:
            return default
        return str(value).strip()
    
    def _get_numeric_value(self, row: pd.Series, column_name: str) -> float:
        """Obtiene valor de celda como número"""
        value = row.get(column_name, 0)
        if pd.isna(value) or value is None:
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

# funcion que usa el controlador
def process_excel_from_content(file_content: bytes, current_user=None) -> Tuple[List[Data_uploadCreate], List[str]]:
  
    processor = ExcelProcessor(current_user)
    return processor.process_excel_content(file_content)