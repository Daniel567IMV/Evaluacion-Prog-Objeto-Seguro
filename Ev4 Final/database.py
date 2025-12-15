import json
import os
import mysql.connector
from mysql.connector import Error

def _load_db_config():
    """Lee el archivo 'config.json' para encontrar los datos de acceso a la base de datos (usuario, contraseña, etc.)."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('MYSQL_CONFIG')
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: No se pudo leer el archivo 'config.json' con los datos de la base de datos: {e}")
        return None

def crear_conexion():
    """
    Usa la configuración que leímos antes para abrir una 'puerta' a la base de datos y poder hablar con ella.
    """
    config = _load_db_config()
    if not config: return None
    try:
        conexion = mysql.connector.connect(**config)

        if conexion.is_connected():
            # Comentamos esto para que no nos llene la consola de mensajes cada vez que nos conectamos.
            return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def crear_tablas_iniciales(conexion):
    """
    Esta función es como un arquitecto: construye las 'estanterías' (tablas) en nuestra base de datos si es que no existen ya.
    """
    cursor = conexion.cursor()
    try:
        # La 'estantería' para guardar los datos de quienes se registran.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL, -- Puede ser un apodo o nombre completo
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            correo VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(50) NOT NULL DEFAULT 'cliente', -- Roles: 'cliente', 'admin'
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        )
        """)
        print("Tabla 'usuarios' creada o ya existente.")

        # La 'estantería' para guardar todos los lugares a los que se puede viajar.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS destinos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            descripcion TEXT,
            actividades TEXT,
            costo INT NOT NULL
        )
        """)
        print("Tabla 'destinos' creada o ya existente.")

        # Aquí guardamos los paquetes, que son como combos de varios destinos.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS paquetes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            fecha_inicio DATE NOT NULL,
            fecha_fin DATE NOT NULL,
            cupos INT NOT NULL DEFAULT 0,
            costo INT NOT NULL DEFAULT 0,
            descripcion TEXT
        )
        """)
        print("Tabla 'paquetes' creada o ya existente.")

        # Esta es una tabla 'puente'. Sirve para saber qué destinos exactos van dentro de cada paquete.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS paquete_destinos (
            paquete_id INT NOT NULL,
            destino_id INT NOT NULL,
            PRIMARY KEY (paquete_id, destino_id),
            FOREIGN KEY (paquete_id) REFERENCES paquetes(id) ON DELETE CASCADE,
            FOREIGN KEY (destino_id) REFERENCES destinos(id) ON DELETE CASCADE
        )
        """)
        print("Tabla 'paquete_destinos' creada o ya existente.")

        # Y aquí apuntamos quién ha reservado qué, ya sea un destino suelto o un paquete completo.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            destino_id INT, -- Puede ser nulo si es una reserva de paquete
            paquete_id INT, -- Puede ser nulo si es una reserva de destino
            fecha_reserva DATE NOT NULL,
            cantidad_personas INT NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (destino_id) REFERENCES destinos(id),
            FOREIGN KEY (paquete_id) REFERENCES paquetes(id) ON DELETE CASCADE
        )
        """)
        print("Tabla 'reservas' creada o ya existente.")

        conexion.commit()
    except Error as e:
        print(f"Error al crear las tablas: {e}")
    finally:
        cursor.close()

def seed_destinos(conexion):
    """
    Esta función es como un 'semillero'. Si la tabla de destinos está vacía, la llena con datos iniciales
    que saca del archivo 'destinos_data.json' para que la aplicación no empiece a cero.
    """
    cursor = conexion.cursor()
    try:
        # 1. Primero, miramos si la tabla ya tiene algo dentro.
        cursor.execute("SELECT COUNT(*) FROM destinos")
        if cursor.fetchone()[0] > 0:
            print("La tabla 'destinos' ya contiene datos. No se agregarán nuevos.")
            return

        # 2. Si está vacía, leemos el archivo JSON y metemos todos esos destinos en la tabla.
        print("Poblando la tabla 'destinos' con datos iniciales...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, 'destinos_data.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            destinos = json.load(f)

        query = "INSERT INTO destinos (id, nombre, descripcion, actividades, costo) VALUES (%s, %s, %s, %s, %s)"
        for d in destinos:
            cursor.execute(query, (d['id'], d['nombre'], d['descripcion'], d['actividades'], d['costo']))
        
        conexion.commit()
        print(f"{len(destinos)} destinos han sido agregados.")

    except Error as e:
        print(f"Error al poblar la base de datos: {e}")
    finally:
        cursor.close()

def seed_paquetes(conexion):
    """
    Igual que la función anterior, pero para los paquetes. Si no hay ninguno, crea unos cuantos de ejemplo.
    """
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM paquetes")
        if cursor.fetchone()[0] > 0:
            print("La tabla 'paquetes' ya contiene datos. No se agregarán nuevos.")
            return

        print("Poblando la tabla 'paquetes' con datos de ejemplo...")
        
        # Creamos unos paquetes de viaje de mentira para que la app tenga algo que mostrar.
        paquetes = [
            ('Maravillas de Europa Clásica', '2026-05-10', '2026-05-20', 25, 4800000, 'Sumérgete en la historia y el romance del viejo continente. Este viaje te llevará desde la Torre Eiffel en París hasta el Coliseo en Roma, pasando por la arquitectura modernista de Barcelona. Disfruta de cenas gourmet, visitas guiadas a museos de clase mundial y paseos al atardecer por calles empedradas llenas de encanto.'),
            ('Aventura Sudamericana', '2026-07-15', '2026-07-25', 15, 3500000, 'Una expedición única que combina la majestuosidad de los Andes con la vibrante cultura latina. Explora las ruinas incas de Cusco, siente el ritmo de la samba en Río de Janeiro y disfruta de un tango en Buenos Aires. Incluye excursiones de senderismo y degustaciones de la mejor gastronomía local.'),
            ('Joyas del Sudeste Asiático', '2026-09-01', '2026-09-12', 20, 2800000, 'Descubre la espiritualidad y los paisajes exóticos de Asia. Navega por la Bahía de Ha-Long, maravíllate con los templos de Angkor Wat en Siem Reap y vive el bullicio de Bangkok. Una experiencia sensorial completa con mercados flotantes, comida callejera increíble y templos dorados.'),
            ('Ruta del Sol Azteca', '2026-11-05', '2026-11-15', 18, 2500000, 'Un viaje a través del tiempo y la naturaleza en México. Desde la vibrante Ciudad de México y sus museos, hasta las relajantes playas de arena blanca en Cancún. Explora antiguas pirámides aztecas y mayas, y sumérgete en cenotes cristalinos bajo la selva.'),
            ('Sueño Americano', '2026-08-10', '2026-08-22', 20, 5200000, 'Vive la experiencia cinematográfica definitiva en Estados Unidos. Pasea por Times Square en Nueva York, busca estrellas en Hollywood, Los Ángeles, y prueba tu suerte en los casinos de Las Vegas. Un recorrido lleno de rascacielos, entretenimiento y cultura pop.'),
            ('Tesoros de Oriente Medio', '2026-10-01', '2026-10-12', 15, 4100000, 'Un viaje místico a la cuna de la civilización. Contempla las Pirámides de Giza en El Cairo, camina por el desfiladero hacia Petra en Jordania y recorre las calles sagradas de Jerusalén. Una inmersión profunda en la historia antigua y la espiritualidad.'),
            ('Escapada Nórdica', '2026-06-15', '2026-06-25', 12, 4500000, 'Descubre la belleza serena de Escandinavia. Navega por los fiordos noruegos desde Oslo, pasea por las coloridas calles de Copenhague y explora el archipiélago de Estocolmo. Un viaje diseñado para amantes del diseño, la naturaleza y la calidad de vida.'),
            ('Safari y Playas de África', '2026-08-05', '2026-08-18', 10, 5500000, 'La combinación perfecta de aventura salvaje y relajación total. Realiza safaris fotográficos en el Serengueti para ver a los "Cinco Grandes" y termina tu viaje descansando en las playas paradisíacas de Zanzíbar con aguas turquesas.'),
            ('Maravillas de Oceanía', '2026-11-20', '2026-12-05', 15, 6200000, 'Explora lo mejor de Australia y Nueva Zelanda. Desde la icónica Ópera de Sídney y los callejones artísticos de Melbourne, hasta los paisajes de película y deportes de aventura en Queenstown. Un viaje al otro lado del mundo que recordarás por siempre.'),
            ('Imperio del Dragón', '2026-09-15', '2026-09-28', 18, 4900000, 'Un recorrido fascinante por la China milenaria y moderna. Camina por la Gran Muralla en Pekín, admira el horizonte futurista de Shanghái y disfruta de la fusión cultural en Hong Kong. Historia, tecnología y gastronomía en un solo viaje.')
        ]
        
        # Ahora le decimos qué destinos van en cada paquete.
        # Nota: Los IDs de paquete (1, 2, 3) se corresponden con el orden de inserción de arriba.
        relaciones = [
            (1, 1003), (1, 1005), (1, 1020), # Paquete 1: París, Roma, Barcelona
            (2, 1002), (2, 1009), (2, 1016), # Paquete 2: Cusco, Río, Buenos Aires
            (3, 1013), (3, 1038), (3, 1039), # Paquete 3: Bangkok, Ha-Long, Siem Reap
            (4, 1048), (4, 1001),            # Paquete 4: CDMX, Cancún
            (5, 1011), (5, 1070), (5, 1069), # Paquete 5: NY, LA, Las Vegas
            (6, 1008), (6, 1097), (6, 1098), # Paquete 6: Cairo, Petra, Jerusalén
            (7, 1062), (7, 1063), (7, 1064), # Paquete 7: Copenhague, Estocolmo, Oslo
            (8, 1043), (8, 1081), (8, 1082), # Paquete 8: Serengueti, Nairobi, Zanzíbar
            (9, 1007), (9, 1057), (9, 1056), # Paquete 9: Sídney, Melbourne, Queenstown
            (10, 1034), (10, 1035), (10, 1036) # Paquete 10: Pekín, Shanghái, Hong Kong
        ]

        # Metemos los paquetes y sus relaciones en la base de datos.
        cursor.executemany("INSERT INTO paquetes (nombre, fecha_inicio, fecha_fin, cupos, costo, descripcion) VALUES (%s, %s, %s, %s, %s, %s)", paquetes)
        cursor.executemany("INSERT INTO paquete_destinos (paquete_id, destino_id) VALUES (%s, %s)", relaciones)
        
        conexion.commit()
        print(f"{len(paquetes)} paquetes de ejemplo han sido agregados.")
    except Error as e:
        print(f"Error al poblar la tabla de paquetes: {e}")
    finally:
        cursor.close()

def inicializar_db_completa():
    """
    Realiza el proceso completo de inicialización:
    1. Crea la base de datos si no existe (conectando primero sin DB).
    2. Crea las tablas.
    3. Carga los datos semilla.
    """
    try:
        db_config = _load_db_config()
        if not db_config:
            print("Error: Configuración no encontrada en config.json.")
            return False

        # 1. Crear Base de Datos (si no existe)
        db_name = db_config.get('database')
        # Copiamos config para conectar al servidor sin especificar DB
        server_config = db_config.copy()
        if 'database' in server_config:
            del server_config['database']
            
        print(f"Conectando al servidor MySQL para verificar la BD '{db_name}'...")
        conn_server = mysql.connector.connect(**server_config)
        cursor = conn_server.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn_server.close()
        print(f"Base de datos '{db_name}' verificada.")

        # 2. Conectar a la BD específica e inicializar tablas/datos
        conn_db = crear_conexion()
        if conn_db:
            crear_tablas_iniciales(conn_db)
            seed_destinos(conn_db)
            seed_paquetes(conn_db)
            conn_db.close()
            return True
        return False

    except Error as e:
        print(f"Error durante la inicialización de la base de datos: {e}")
        return False

# Este bloque de código solo se ejecuta si abres este archivo directamente (y no desde otro).
# Su misión es preparar toda la base de datos desde cero.
if __name__ == '__main__':
    try:
        db_config = _load_db_config()
        if not db_config:
            raise Exception("La configuración de la base de datos no se encontró en config.json")

        # 1. Nos conectamos al programa MySQL, pero sin elegir una base de datos todavía.
        db_name = db_config.pop('database') # Quitamos temporalmente el nombre de la BD
        conn_server = mysql.connector.connect(**db_config)
        cursor = conn_server.cursor()

        # 2. Le pedimos que cree nuestra base de datos si no la encuentra.
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"Base de datos '{db_name}' creada o ya existente.")
        conn_server.close()

        # 3. Ahora sí, nos conectamos a nuestra base de datos específica para empezar a trabajar.
        conn_db = crear_conexion()
        if conn_db:
            print("Inicializando tablas...")
            crear_tablas_iniciales(conn_db)
            # Después de crear las tablas, poblamos los datos iniciales
            seed_destinos(conn_db)
            seed_paquetes(conn_db)
            conn_db.close()
            print("Inicialización de la base de datos completada.")

    except Error as e:
        print(f"Ocurrió un error durante la inicialización: {e}")
