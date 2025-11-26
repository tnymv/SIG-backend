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
            # Leer las primeras filas para extraer información del encabezado
            header_df = pd.read_excel(file_content, nrows=8, header=None)
            
            # Extraer información del encabezado
            report_date = None
            report_hour = None
            report_seriereport = None
            report_user = None
            report_municipality = None
            report_department = None
            
            # Buscar en las primeras 8 filas
            for idx, row in header_df.iterrows():
                # Unir todas las celdas de la fila en un string
                row_cells = [str(cell) for cell in row.values if pd.notna(cell) and str(cell).strip()]
                row_str = ' '.join(row_cells).upper()
                
                # Debug: imprimir cada fila para ver qué contiene
                if idx < 5:  # Solo imprimir las primeras 5 filas para debug
                    print(f"Fila {idx}: {row_str[:200]}")  # Limitar a 200 caracteres
                
                # Buscar fecha (formato: Fecha:25/08/2025 o similar)
                if 'FECHA:' in row_str:
                    fecha_match = row_str.split('FECHA:')
                    if len(fecha_match) > 1:
                        fecha_str = fecha_match[1].strip().split()[0]  # Tomar solo la fecha
                        try:
                            # Intentar parsear diferentes formatos de fecha
                            if '/' in fecha_str:
                                parts = fecha_str.split('/')
                                if len(parts) == 3:
                                    day, month, year = parts
                                    report_date = datetime(int(year), int(month), int(day))
                        except:
                            pass
                
                # Buscar hora (formato: Hora:16:23 o similar)
                if 'HORA:' in row_str:
                    hora_match = row_str.split('HORA:')
                    if len(hora_match) > 1:
                        hora_str = hora_match[1].strip().split()[0]  # Tomar solo la hora
                        try:
                            if ':' in hora_str:
                                parts = hora_str.split(':')
                                if len(parts) >= 2:
                                    hour_val = int(parts[0])
                                    minute_val = int(parts[1])
                                    report_hour = datetime.now().replace(hour=hour_val, minute=minute_val, second=0, microsecond=0).time()
                        except:
                            pass
                
                # Buscar seriereport (formato: Reporte: R00809001.rpt)
                if 'REPORTE:' in row_str and '.RPT' in row_str:
                    report_match = row_str.split('REPORTE:')
                    if len(report_match) > 1:
                        report_seriereport = report_match[1].strip().split()[0]
                
                # Buscar usuario (formato: Usuario:CAMACHO)
                if 'USUARIO:' in row_str:
                    user_match = row_str.split('USUARIO:')
                    if len(user_match) > 1:
                        report_user = user_match[1].strip().split()[0]
                
                # Buscar municipio (formato: MUNICIPALIDAD DE PALESTINA DE LOS ALTOS)
                # Puede estar en una celda completa o en múltiples celdas
                if 'MUNICIPALIDAD' in row_str and 'DE' in row_str:
                    # Buscar el patrón "MUNICIPALIDAD DE" seguido del nombre
                    if 'MUNICIPALIDAD DE' in row_str:
                        municipio_match = row_str.split('MUNICIPALIDAD DE')
                        if len(municipio_match) > 1:
                            # Tomar todo después de "MUNICIPALIDAD DE"
                            municipio_text = municipio_match[1].strip()
                            # Si hay "DEPARTAMENTO" después, cortar ahí
                            if 'DEPARTAMENTO' in municipio_text:
                                municipio_text = municipio_text.split('DEPARTAMENTO')[0].strip()
                            # Eliminar cualquier texto después de palabras clave como "HORA:", "FECHA:", "REPORTE:", "USUARIO:"
                            for keyword in ['HORA:', 'FECHA:', 'REPORTE:', 'USUARIO:', 'CLASIFICACIÓN', 'INSTITUCIONAL']:
                                if keyword in municipio_text:
                                    municipio_text = municipio_text.split(keyword)[0].strip()
                            # Limpiar espacios múltiples y caracteres especiales
                            municipio_text = ' '.join(municipio_text.split())
                            if municipio_text and len(municipio_text) > 3:  # Validar que tenga contenido real
                                report_municipality = municipio_text
                
                # Buscar departamento (formato: DEPARTAMENTO DE QUETZALTENANGO)
                if 'DEPARTAMENTO DE' in row_str:
                    depto_match = row_str.split('DEPARTAMENTO DE')
                    if len(depto_match) > 1:
                        depto_text = depto_match[1].strip()
                        # Eliminar cualquier texto después de palabras clave
                        for keyword in ['HORA:', 'FECHA:', 'REPORTE:', 'USUARIO:', 'CLASIFICACIÓN', 'INSTITUCIONAL', 'MUNICIPALIDAD']:
                            if keyword in depto_text:
                                depto_text = depto_text.split(keyword)[0].strip()
                        # Limpiar espacios múltiples
                        depto_text = ' '.join(depto_text.split())
                        if depto_text and len(depto_text) > 3:  # Validar que tenga contenido real
                            report_department = depto_text
            
            # Leer Excel saltando encabezados (desde la fila 9)
            df = pd.read_excel(file_content, skiprows=8)
            print(f" Excel procesado: {len(df)} filas encontradas")
            print(f"Columnas detectadas: {list(df.columns)}")
            print(f"Fecha: {report_date}, Hora: {report_hour}, Serie: {report_seriereport}, Usuario: {report_user}, Municipio: {report_municipality}, Departamento: {report_department}")
            
            # Normalizar nombres de columnas (eliminar espacios y convertir a mayúsculas)
            df.columns = df.columns.str.strip().str.upper()
            
            # Mapear posibles variaciones de nombres de columnas
            column_mapping = {
                'IDENTIFICA': 'IDENTIFICA',
                'IDENTIFICADOR': 'IDENTIFICA',
                'ID': 'IDENTIFICA',
                'CONTRIBUYENTE': 'CONTRIBUYENTE',
                'COLONIA': 'COLONIA',
                'CAT_SERVICIO': 'CAT_SERVICIO',
                'CATEGORIA': 'CAT_SERVICIO',
                'CANON': 'CANON',
                'EXCESO': 'EXCESO',
                'TOTAL': 'TOTAL'
            }
            
            # Renombrar columnas según el mapeo
            for old_name, new_name in column_mapping.items():
                if old_name in df.columns and new_name not in df.columns:
                    df.rename(columns={old_name: new_name}, inplace=True)
            
            # Validar que el archivo tenga las columnas necesarias
            required_columns = ['CONTRIBUYENTE', 'COLONIA']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                error_msg = f"El archivo Excel no tiene las columnas requeridas: {', '.join(missing_columns)}. Columnas encontradas: {', '.join(df.columns.tolist())}"
                self.errors.append(error_msg)
                print(f"Error: {error_msg}")
                return [], self.errors
            
            # Procesar cada fila
            for index, row in df.iterrows():
                row_errors = self._validate_row(row, index + 9)
                
                if not row_errors:
                    # Preparar datos para Data_uploadCreate
                    data_dict = {
                        # Encabezado - usar datos del Excel si están disponibles
                        "siaf": "SERVICIOSGL",
                        "municipality": report_municipality,
                        "department": report_department,
                        "institutional_classification": 12100924,
                        "report": "Morosidad Servicio De Agua", 
                        "date": report_date if report_date else datetime.now(),
                        "hour": report_hour if report_hour else datetime.now().time(),
                        "seriereport": report_seriereport if report_seriereport else "R00809001.rpt",
                        "user": report_user if report_user else (self.current_user.user if self.current_user else "SYSTEM"),
                        "status": True,
                        # Datos del Excel - usar IDENTIFICA (como en el Excel)
                        "identifier": self._get_cell_value(row, 'IDENTIFICA', f"AUTO-{index+9}"),
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
            
        except pd.errors.EmptyDataError:
            error_msg = "El archivo Excel está vacío o no tiene datos válidos"
            self.errors.append(error_msg)
            print(f"Error: {error_msg}")
            return [], self.errors
        except pd.errors.ParserError as e:
            error_msg = f"Error al leer el archivo Excel. Verifica que sea un archivo Excel válido: {str(e)}"
            self.errors.append(error_msg)
            print(f"Error: {error_msg}")
            return [], self.errors
        except KeyError as e:
            error_msg = f"El archivo Excel no tiene el formato esperado. Columna faltante: {str(e)}"
            self.errors.append(error_msg)
            print(f"Error: {error_msg}")
            return [], self.errors
        except Exception as e:
            error_msg = f"Error al procesar archivo Excel: {str(e)}"
            self.errors.append(error_msg)
            print(f"Error: {error_msg}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
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