# SIG-backend

Sistema de Información Geográfica (SIG) desarrollado para la Municipalidad de Palestina de Los Altos. Una aplicación web moderna construida con React que proporciona herramientas de gestión y visualización de información geográfica.

## 🚀 Características

- **API moderna y de alto rendimiento** basada en ASGI
- **Validación automática** de datos con tipado fuerte gracias a Pydantic
- **Documentación interactiva** generada automáticamente con Swagger UI y ReDoc
- **Sistema de rutas flexible** con soporte para parámetros dinámicos y dependencias
- **Soporte para WebSockets y middleware personalizado** para ampliar funcionalidades
- **Diseño modular y escalable** ideal para proyectos pequeños o grandes

## 📋 Requisitos del Sistema

### Requisitos Mínimos
- **Python**: 3.8 o superio.
- **pip**: Última versión recomendada.
- **Servidor ASGI**: Uvicorn o similar.

### Requisitos Recomendados
- **Python**: 3.11 o 3.12
- **Entorno virtual**: venv
- **RAM**: 4GB mínimo, 8GB recomendado
- **Espacio en disco**: 2GB libres

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd SIG-backtend
```

### 2. Instalar dependencias
```bash
pip install requirements.txt
```

### 3. crear entorno virtual
```bash
python -m venv .venv 
```

### 4. Inicar el entorno virtual
```bash
.venv\Scripts\Activate.ps1
```

### 5. Ejecutar el proyecto
```bash 
uvicorn main:app --reload
```
El proyecto se ejecutará en `http://localhost:3000`

## 📜 Scripts Disponibles

| Comando | Descripción |
|---------|-------------|
| `uvicorn main:app --reload` | Inicia el servidor en modo desarrollo con recarga automática |
| `uvicorn main:app --host 0.0.0.0 --port 8000` | Ejecuta la app en un host y puerto específicos para producción básica |
| `pip freeze > requirements.txt` | Genera el archivo de dependencias actuales |
| `pip install -r requirements.txt` | Instala las dependencias desde el archivo requirements.txt |
| `pytest` | Ejecuta las pruebas unitarias del proyecto |
| `pip install (nombre de dependecia)` | Para instalar un dependecia individual |



## 🏗️ Estructura del Proyecto

```
app/
├── controllers/       # Controladores o routers donde defines las rutas de la API
     └──
├── db/                # Configuración y conexión a la base de datos
     └──
├── models/            # Modelos de datos o de ORM
     └──
├── schemas/           # Esquemas Pydantic para validación y serialización de datos
     └──
├── utils/             # Funciones auxiliares o utilidades generales
     └──
└── main.py            # Punto de entrada principal de la aplicación FastAPI
```

## 🎨 Tecnologías Utilizadas

### Backend
- **FastAPI 0.115.0** - Framework principal para construir APIs rápidas y modernas
- **Uvicorn 0.30.1** - Servidor ASGI para ejecutar la aplicación
- **SQLAlchemy 2.x** - ORM para manejar bases de datos relacionales
- **Pydantic 2.x** - Validación y serialización de datos
- **Alembic 1.x** - Migraciones de base de datos
- **Databases 0.7.x** - Conexión asíncrona a bases de datos (opcional)
- **Passlib 1.7.x** - Manejo seguro de contraseñas

### Herramientas de Desarrollo
- **pytest 7.x** - Framework de pruebas unitarias.
- **httpx 0.24.x** - Cliente HTTP para pruebas o consumo de APIs.
- **python-dotenv 1.x** - Manejo de variables de entorno.

## 🌐 Despliegue

### Despliegue en Supabase
1. Crea un proyecto en Supabase y configura tu base de datos PostgreSQL.
2. Obtén la URL de la base de datos y la API Key desde el panel de Supabase.
3. Configura tu proyecto FastAPI para conectarse a la base de datos usando las credenciales
    Guardar en un archivo .env
    Usar SQLAlchemy, Databases o Pydantic para manejar la conexión.
4. Ejecuta tu aplicación localmente con: uvicorn main:app --reload
5. Para producción, despliega tu FastAPI en un host externo (Render, Heroku, Railway, Docker) y conecta tu aplicación a la base de datos de Supabase.
6. Configura CORS en FastAPI para permitir que tu frontend se comunique con tu backend

## 🐛 Solución de Problemas

### Error: "Module not found / Package missing"
```bash
# Asegúrate de instalar las dependencias
    pip install -r requirements.txt

```

### Error: "Port already in use"
```bash
# En macOS/Linux
lsof -ti:8000 | xargs kill -9

# En Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

```

### Error de permisos al instalar paquetes
```bash
# En macOS/Linux
sudo pip install <package_name>

# Alternativa recomendada: usar entorno virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## 📞 Soporte

Para reportar problemas o solicitar nuevas características:
1. Crear un issue en el repositorio
2. Describir el problema detalladamente
3. Incluir pasos para reproducir el error
4. Especificar versión de Python, FastAPI, y dependencias relevantes.

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Contribuidores

- Wilber
- Mendel  
- Carlos
- Edwin

---

**Desarrollado con ❤️ para la Municipalidad de Palestina de Los Altos**
