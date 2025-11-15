"""
Script para poblar la base de datos con datos de prueba de Palestina de los Altos, Quetzaltenango

Uso:
    python seed_palestina.py
"""
from app.db.database import SessionLocal
from datetime import datetime, timedelta
import random
import math
from geoalchemy2 import WKTElement
from sqlalchemy import func, text

# Importar modelos
from app.models.type_employee.type_employees import TypeEmployee
from app.models.employee.employee import Employee
from app.models.rol.rol import Rol
from app.models.user.user import Username
from app.models.tanks.tanks import Tank
from app.models.pipes.pipes import Pipes
from app.models.connection.connections import Connection
from app.models.interventions.interventions import Interventions
from app.models.intervention_entities.intervention_entities import Intervention_entities
from app.models.files.files import Files
from app.models.pipes.pipe_connections import pipe_connections
from app.models.tanks.tanks_pipes import tank_pipes
from app.utils.auth import get_password_hash


# ========== CONFIGURACIÓN ==========
PALESTINA_CENTER_LAT = 14.931944
PALESTINA_CENTER_LON = -91.693889

NOMBRES_M = ["Juan", "José", "Carlos", "Luis", "Miguel", "Pedro", "Jorge", "Manuel"]
NOMBRES_F = ["María", "Rosa", "Ana", "Carmen", "Elena", "Lucía", "Isabel", "Marta"]
APELLIDOS = ["García", "López", "Martínez", "González", "Pérez", "Rodríguez", "Morales", "Hernández"]
COLONIAS = ["Cabecera Municipal", "Aldea Paquix", "Caserío El Centro", "Aldea Chitay", "Caserío San José"]
MATERIALES = ["PVC", "HG", "PEAD"]


# ========== FUNCIONES AUXILIARES ==========
def generar_coordenada(lat_center, lon_center, radio_km):
    """Genera coordenada aleatoria dentro de un radio"""
    radio_grados = radio_km / 111.0
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(0, radio_grados)
    lat = lat_center + (distance * math.cos(angle))
    lon = lon_center + (distance * math.sin(angle))
    return round(lat, 6), round(lon, 6)


def calcular_distancia(lat1, lon1, lat2, lon2):
    """Calcula distancia entre dos coordenadas en km"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


# ========== FUNCIONES DE CREACIÓN ==========
def crear_tipos_empleados(db):
    """Crea tipos de empleados"""
    tipos = [
        {"name": "Operador de Campo", "description": "Encargado de operaciones en campo"},
        {"name": "Técnico", "description": "Técnico especializado en mantenimiento"},
        {"name": "Supervisor", "description": "Supervisor de operaciones"},
        {"name": "Fontanero", "description": "Fontanero especializado"}
    ]
    
    tipos_creados = {}
    for tipo_data in tipos:
        tipo = db.query(TypeEmployee).filter(TypeEmployee.name == tipo_data["name"]).first()
        if not tipo:
            tipo = TypeEmployee(**tipo_data, state=True)
            db.add(tipo)
            db.flush()
        tipos_creados[tipo_data["name"]] = tipo
    
    print(f"✅ Tipos de empleados: {len(tipos_creados)}")
    return tipos_creados


def crear_empleados(db, tipos_empleados):
    """Crea empleados guatemaltecos"""
    empleados = []
    tipo_list = list(tipos_empleados.values())
    
    for i in range(10):
        nombre = random.choice(NOMBRES_M if random.random() > 0.5 else NOMBRES_F)
        apellido = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
        telefono = f"{'7' if random.random() > 0.5 else '3'}{random.randint(1000000, 9999999)}"
        
        empleado = Employee(
            first_name=nombre,
            last_name=apellido,
            phone_number=telefono,
            id_type_employee=random.choice(tipo_list).id_type_employee,
            state=True
        )
        db.add(empleado)
        db.flush()
        empleados.append(empleado)
    
    print(f"✅ Empleados creados: {len(empleados)}")
    return empleados


def crear_roles(db):
    """Crea roles del sistema"""
    roles_data = [
        {"name": "Supervisor", "description": "Supervisor general del sistema"},
        {"name": "Técnico", "description": "Técnico de campo"},
        {"name": "Usuario", "description": "Usuario básico"}
    ]
    
    roles = []
    for rol_data in roles_data:
        rol = db.query(Rol).filter(Rol.name == rol_data["name"]).first()
        if not rol:
            rol = Rol(**rol_data, status=True)
            db.add(rol)
            db.flush()
        roles.append(rol)
    
    print(f"✅ Roles creados: {len(roles)}")
    return roles


def crear_usuarios(db, empleados, roles):
    """Crea usuarios"""
    usuarios = []
    for i, empleado in enumerate(empleados[:7]):
        usuario = Username(
            user=f"{empleado.first_name.lower()}.{empleado.last_name.split()[0].lower()}",
            password_hash=get_password_hash("password123"),
            email=f"{empleado.first_name.lower()}.{empleado.last_name.split()[0].lower()}.{empleado.id_employee}@palestina.gob.gt",
            employee_id=empleado.id_employee,
            rol_id=roles[i % len(roles)].id_rol,
            status=True
        )
        db.add(usuario)
        db.flush()
        usuarios.append(usuario)
    
    print(f"✅ Usuarios creados: {len(usuarios)}")
    return usuarios


def crear_tanques(db):
    """Crea 10 tanques distribuidos en Palestina"""
    tanques_data = [
        {"name": "Tanque Central", "offset_lat": 0.0, "offset_lon": 0.0, "colonia": "Cabecera Municipal"},
        {"name": "Tanque Paquix Norte", "offset_lat": 0.015, "offset_lon": -0.01, "colonia": "Aldea Paquix"},
        {"name": "Tanque Paquix Sur", "offset_lat": 0.01, "offset_lon": -0.015, "colonia": "Aldea Paquix"},
        {"name": "Tanque Chitay", "offset_lat": -0.012, "offset_lon": 0.018, "colonia": "Aldea Chitay"},
        {"name": "Tanque San José", "offset_lat": 0.008, "offset_lon": 0.020, "colonia": "Caserío San José"},
        {"name": "Tanque El Centro", "offset_lat": -0.018, "offset_lon": -0.008, "colonia": "Caserío El Centro"},
        {"name": "Tanque La Esperanza", "offset_lat": 0.020, "offset_lon": 0.005, "colonia": "Caserío La Esperanza"},
        {"name": "Tanque Monte Verde", "offset_lat": -0.015, "offset_lon": 0.012, "colonia": "Caserío Monte Verde"},
        {"name": "Tanque Las Flores", "offset_lat": 0.005, "offset_lon": -0.020, "colonia": "Caserío Las Flores"},
        {"name": "Tanque Buena Vista", "offset_lat": -0.010, "offset_lon": -0.015, "colonia": "Caserío Buena Vista"}
    ]
    
    tanques = []
    for i, tanque_data in enumerate(tanques_data):
        # Verificar si ya existe
        existe = db.query(Tank).filter(Tank.name == tanque_data["name"]).first()
        if existe:
            print(f"   ⚠️  {tanque_data['name']} ya existe, omitiendo...")
            tanques.append(existe)
            continue
        
        lat = PALESTINA_CENTER_LAT + tanque_data["offset_lat"]
        lon = PALESTINA_CENTER_LON + tanque_data["offset_lon"]
        
        # Usar WKTElement para las coordenadas (igual que en el controlador)
        tanque = Tank(
            name=tanque_data["name"],
            coordinates=WKTElement(f"POINT({lon} {lat})", srid=4326),
            connections=tanque_data["colonia"],
            photography=[],
            state=True
        )
        db.add(tanque)
        db.flush()
        tanques.append(tanque)
        
        # Mostrar coordenadas para verificar
        print(f"   • {tanque_data['name']}: LAT={lat:.6f}, LON={lon:.6f}")
    
    print(f"✅ Tanques creados/encontrados: {len(tanques)}")
    return tanques


def crear_red_tuberias(db, tanques):
    """Crea red de 150+ tuberías y conexiones"""
    tuberias = []
    conexiones = []
    
    # Extraer coordenadas de tanques usando funciones PostGIS
    tanques_coords = []
    for tanque in tanques:
        # Usar ST_X y ST_Y para extraer coordenadas
        lon, lat = db.query(
            func.ST_X(tanque.coordinates),
            func.ST_Y(tanque.coordinates)
        ).first()
        tanques_coords.append((lat, lon, tanque))
        print(f"   📍 {tanque.name}: LAT={lat:.6f}, LON={lon:.6f}")
    
    print("\n🔧 Creando red de tuberías...")
    
    # Por cada tanque crear ramas
    for tanque_lat, tanque_lon, tanque in tanques_coords:
        num_ramas = random.randint(15, 20)
        
        for rama in range(num_ramas):
            # Punto inicial cerca del tanque
            inicio_lat, inicio_lon = generar_coordenada(tanque_lat, tanque_lon, 0.1)
            
            # Crear segmentos
            num_segmentos = random.randint(2, 4)
            lat_actual, lon_actual = inicio_lat, inicio_lon
            
            for segmento in range(num_segmentos):
                # Punto siguiente
                lat_siguiente, lon_siguiente = generar_coordenada(lat_actual, lon_actual, 0.3)
                
                # Evitar otros tanques
                distancia_minima = min([
                    calcular_distancia(lat_siguiente, lon_siguiente, t_lat, t_lon)
                    for t_lat, t_lon, _ in tanques_coords if (t_lat, t_lon) != (tanque_lat, tanque_lon)
                ])
                
                if distancia_minima < 0.2:
                    lat_siguiente, lon_siguiente = generar_coordenada(lat_actual, lon_actual, 0.2)
                
                # Crear conexión
                conexion = Connection(
                    coordenates=WKTElement(f"POINT({lon_actual} {lat_actual})", srid=4326),
                    material=random.choice(MATERIALES),
                    diameter_mn=random.choice([1.5, 2.0, 2.5, 3.0]),
                    pressure_nominal=f"{random.choice([40, 60, 80, 100])} PSI",
                    connection_type=random.choice(["Codo", "T", "Cruz", "Reducción"]),
                    depth_m=random.uniform(0.5, 1.5),
                    installed_date=datetime.now() - timedelta(days=random.randint(30, 1800)),
                    installed_by=f"Cuadrilla {random.randint(1, 5)}",
                    description=f"Conexión en {random.choice(COLONIAS)}",
                    state=True
                )
                db.add(conexion)
                db.flush()
                conexiones.append(conexion)
                
                # Crear tubería
                tuberia = Pipes(
                    material=random.choice(MATERIALES),
                    diameter=random.choice([1.0, 1.5, 2.0, 2.5, 3.0]),
                    size=calcular_distancia(lat_actual, lon_actual, lat_siguiente, lon_siguiente),
                    installation_date=datetime.now() - timedelta(days=random.randint(30, 1800)),
                    coordinates=WKTElement(f"LINESTRING({lon_actual} {lat_actual}, {lon_siguiente} {lat_siguiente})", srid=4326),
                    observations=f"Tubería en {random.choice(COLONIAS)}",
                    status=True
                )
                db.add(tuberia)
                db.flush()
                tuberias.append(tuberia)
                
                # Relacionar tubería con conexión
                db.execute(
                    pipe_connections.insert().values(
                        pipe_id=tuberia.id_pipes,
                        connection_id=conexion.id_connection
                    )
                )
                
                lat_actual, lon_actual = lat_siguiente, lon_siguiente
                
                # 30% ramificación secundaria
                if random.random() < 0.3:
                    lat_rama, lon_rama = generar_coordenada(lat_actual, lon_actual, 0.2)
                    
                    conexion_rama = Connection(
                        coordenates=WKTElement(f"POINT({lon_actual} {lat_actual})", srid=4326),
                        material=random.choice(MATERIALES),
                        diameter_mn=random.choice([1.0, 1.5, 2.0]),
                        pressure_nominal=f"{random.choice([40, 60, 80])} PSI",
                        connection_type="T",
                        depth_m=random.uniform(0.5, 1.2),
                        installed_date=datetime.now() - timedelta(days=random.randint(30, 1800)),
                        installed_by=f"Cuadrilla {random.randint(1, 5)}",
                        description=f"Derivación en {random.choice(COLONIAS)}",
                        state=True
                    )
                    db.add(conexion_rama)
                    db.flush()
                    conexiones.append(conexion_rama)
                    
                    tuberia_rama = Pipes(
                        material=random.choice(MATERIALES),
                        diameter=random.choice([0.75, 1.0, 1.5]),
                        size=calcular_distancia(lat_actual, lon_actual, lat_rama, lon_rama),
                        installation_date=datetime.now() - timedelta(days=random.randint(30, 1800)),
                        coordinates=WKTElement(f"LINESTRING({lon_actual} {lat_actual}, {lon_rama} {lat_rama})", srid=4326),
                        observations=f"Rama secundaria en {random.choice(COLONIAS)}",
                        status=True
                    )
                    db.add(tuberia_rama)
                    db.flush()
                    tuberias.append(tuberia_rama)
                    
                    db.execute(
                        pipe_connections.insert().values(
                            pipe_id=tuberia_rama.id_pipes,
                            connection_id=conexion_rama.id_connection
                        )
                    )
        
        # Relacionar tuberías con tanque
        for tuberia in tuberias[-num_ramas:]:
            if random.random() < 0.4:
                db.execute(
                    tank_pipes.insert().values(
                        tank_id=tanque.id_tank,
                        pipe_id=tuberia.id_pipes
                    )
                )
    
    print(f"✅ Tuberías creadas: {len(tuberias)}")
    print(f"✅ Conexiones creadas: {len(conexiones)}")
    return tuberias, conexiones


def crear_intervenciones(db, tanques, tuberias, conexiones):
    """Crea intervenciones históricas"""
    tipos_int = ["Mantenimiento preventivo", "Reparación de fuga", "Instalación nueva", 
                 "Cambio de tubería", "Limpieza de tanque", "Reparación de válvula"]
    
    intervenciones = []
    
    for i in range(50):
        fecha_inicio = datetime.now() - timedelta(days=random.randint(1, 730))
        duracion = timedelta(hours=random.randint(2, 48))
        
        intervencion = Interventions(
            description=f"{random.choice(tipos_int)} en {random.choice(COLONIAS)}",
            start_date=fecha_inicio,
            end_date=fecha_inicio + duracion,
            status=random.choice([True, False]),
            photography=[]
        )
        db.add(intervencion)
        db.flush()
        intervenciones.append(intervencion)
        
        # Relacionar con entidades
        tipo_entidad = random.choice(["tanque", "tuberia", "conexion"])
        
        if tipo_entidad == "tanque":
            entidad = Intervention_entities(
                d_interventions=intervencion.id_interventions,
                id_tank=random.choice(tanques).id_tank
            )
        elif tipo_entidad == "tuberia":
            entidad = Intervention_entities(
                d_interventions=intervencion.id_interventions,
                id_pipes=random.choice(tuberias).id_pipes
            )
        else:
            entidad = Intervention_entities(
                d_interventions=intervencion.id_interventions,
                id_connection=random.choice(conexiones).id_connection
            )
        
        db.add(entidad)
    
    print(f"✅ Intervenciones creadas: {len(intervenciones)}")
    return intervenciones


def crear_archivos(db):
    """Crea archivos de contribuyentes"""
    archivos = []
    categorias = ["Residencial", "Comercial", "Industrial", "Institucional"]
    
    for i in range(80):
        nombre = f"{random.choice(NOMBRES_M + NOMBRES_F)} {random.choice(APELLIDOS)}"
        
        archivo = Files(
            taxpayer=nombre,
            cologne=random.choice(COLONIAS),
            cat_service=random.choice(categorias),
            canon=random.choice([25, 30, 35, 40, 50, 75, 100]),
            excess=random.uniform(0, 50),
            total=random.randint(25, 150),
            status=True
        )
        db.add(archivo)
        db.flush()
        archivos.append(archivo)
    
    print(f"✅ Archivos creados: {len(archivos)}")
    return archivos


# ========== FUNCIÓN PRINCIPAL ==========
def limpiar_datos(db):
    """Limpia datos de infraestructura existentes"""
    print("🗑️  Limpiando datos existentes...")
    
    try:
        # Eliminar en orden inverso de dependencias
        print("   Eliminando intervention_entities...")
        db.query(Intervention_entities).delete()
        
        print("   Eliminando interventions...")
        db.query(Interventions).delete()
        
        print("   Eliminando files...")
        db.query(Files).delete()
        
        print("   Eliminando relaciones pipe_connections...")
        db.execute(text("DELETE FROM pipe_connections"))
        
        print("   Eliminando relaciones tank_pipes...")
        db.execute(text("DELETE FROM tank_pipes"))
        
        print("   Eliminando connections...")
        db.query(Connection).delete()
        
        print("   Eliminando pipes...")
        db.query(Pipes).delete()
        
        print("   Eliminando tanks...")
        db.query(Tank).delete()
        
        db.commit()
        print("✅ Datos limpiados exitosamente\n")
    except Exception as e:
        db.rollback()
        print(f"❌ Error al limpiar: {e}\n")
        raise


def main():
    print("\n" + "="*70)
    print("🌱 SEED - PALESTINA DE LOS ALTOS, QUETZALTENANGO")
    print("="*70 + "\n")
    
    # Preguntar si limpiar datos
    respuesta = input("¿Deseas limpiar los datos existentes antes de crear nuevos? (s/n): ").lower()
    limpiar = respuesta == 's'
    print()
    
    db = SessionLocal()
    
    try:
        if limpiar:
            limpiar_datos(db)
        
        print("📍 Coordenadas centro: 14.931944°N, -91.693889°W\n")
        
        # Crear datos
        tipos_empleados = crear_tipos_empleados(db)
        empleados = crear_empleados(db, tipos_empleados)
        roles = crear_roles(db)
        usuarios = crear_usuarios(db, empleados, roles)
        tanques = crear_tanques(db)
        tuberias, conexiones = crear_red_tuberias(db, tanques)
        intervenciones = crear_intervenciones(db, tanques, tuberias, conexiones)
        archivos = crear_archivos(db)
        
        # Commit
        db.commit()
        
        print("\n" + "="*70)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("="*70)
        print(f"\n📊 RESUMEN:")
        print(f"   • Tipos de empleados: {len(tipos_empleados)}")
        print(f"   • Empleados: {len(empleados)}")
        print(f"   • Roles: {len(roles)}")
        print(f"   • Usuarios: {len(usuarios)}")
        print(f"   • Tanques: {len(tanques)}")
        print(f"   • Tuberías: {len(tuberias)}")
        print(f"   • Conexiones: {len(conexiones)}")
        print(f"   • Intervenciones: {len(intervenciones)}")
        print(f"   • Archivos: {len(archivos)}")
        print(f"\n   TOTAL: ~{len(tuberias) + len(conexiones) + len(tanques) + len(intervenciones) + len(archivos)} registros")
        print("\n🎉 ¡Base de datos lista para pruebas!\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {str(e)}\n")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

