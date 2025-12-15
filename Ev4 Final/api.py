import requests
import mysql.connector
import random
import json
import os

def _load_api_key():
    """Carga la clave de API desde el archivo de configuración."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('OPENTRIPMAP_API_KEY')
    except FileNotFoundError:
        return None

def _get_destinos_from_local_json():
    """
    Función de fallback: obtiene los destinos desde el archivo JSON local.
    """
    print("ADVERTENCIA: Usando datos locales (fallback). La API no está disponible o la clave no es válida.")
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, 'destinos_data.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: No se encontró el archivo de fallback destinos_data.json.")
        return []

from database import crear_conexion

def get_destinos(termino_busqueda=None):
    """
    Obtiene destinos desde la base de datos local.
    Si hay un término de búsqueda, filtra por nombre.
    Devuelve una tupla: (lista_de_destinos, fuente_de_datos).
    """
    conn = crear_conexion()
    if not conn:
        return _get_destinos_from_local_json(), "Local (Fallback)"

    cursor = conn.cursor(dictionary=True)
    try:
        if termino_busqueda:
            query = "SELECT * FROM destinos WHERE nombre LIKE %s"
            cursor.execute(query, (f"%{termino_busqueda}%",))
        else:
            query = "SELECT * FROM destinos"
            cursor.execute(query)
        
        destinos = cursor.fetchall()
        return destinos, "Database"
    except mysql.connector.Error as e:
        print(f"Error al obtener destinos de la BD: {e}")
        return _get_destinos_from_local_json(), "Local (Fallback)"
    finally:
        cursor.close()
        conn.close()

def get_paquetes():
    """
    Endpoint de la API para obtener todos los paquetes con sus detalles desde la BD local.
    """
    conn = crear_conexion()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT p.id, p.nombre, p.fecha_inicio, p.fecha_fin, p.cupos,
                   GROUP_CONCAT(d.nombre SEPARATOR ', ') AS destinos,
                   SUM(d.costo) AS costo_total
            FROM paquetes p
            JOIN paquete_destinos pd ON p.id = pd.paquete_id
            JOIN destinos d ON pd.destino_id = d.id
            GROUP BY p.id, p.nombre, p.fecha_inicio, p.fecha_fin
            ORDER BY p.id;
        """
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error en la API al obtener paquetes: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# --- Sincronización con API Externa ---

def sync_destinos_from_api():
    """
    Obtiene destinos de la API de OpenTripMap y los guarda/actualiza en la BD local.
    """
    api_key = _load_api_key()
    if not api_key or api_key == "TU_API_KEY_AQUI":
        print("ADVERTENCIA: No se puede sincronizar. La clave de API no está configurada.")
        return False, "Clave API no válida"

    ciudades = ["Paris", "Rome", "Tokyo", "New York", "London", "Cusco", "Sydney", "Cairo"]
    random.shuffle(ciudades)
    ciudades_a_buscar = ciudades[:5] # Sincronizamos 5 ciudades aleatorias

    conn = crear_conexion()
    if not conn: return False, "Sin conexión a BD"
    cursor = conn.cursor()

    destinos_agregados = 0
    try:
        for ciudad in ciudades_a_buscar:
            geo_url = f"http://api.opentripmap.com/0.1/en/places/geoname?name={ciudad}&apikey={api_key}"
            geo_response = requests.get(geo_url, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()

            if 'lon' not in geo_data: continue

            places_url = f"http://api.opentripmap.com/0.1/en/places/radius?radius=5000&lon={geo_data['lon']}&lat={geo_data['lat']}&kinds=interesting_places&limit=5&apikey={api_key}"
            places_response = requests.get(places_url, timeout=10)
            places_response.raise_for_status()
            places_data = places_response.json()

            if not places_data.get('features'): continue

            nombres_atracciones = [p['properties']['name'] for p in places_data['features'] if p['properties']['name']]
            if not nombres_atracciones: continue

            # Usamos INSERT ... ON DUPLICATE KEY UPDATE para insertar o actualizar si el ID ya existe.
            # Esto requiere que 'id' sea PRIMARY KEY o UNIQUE.
            query = """
                INSERT INTO destinos (id, nombre, descripcion, actividades, costo)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                nombre=VALUES(nombre), descripcion=VALUES(descripcion), actividades=VALUES(actividades), costo=VALUES(costo)
            """
            datos_destino = (
                geo_data.get('geonameId'),
                f"{geo_data['name']}, {geo_data['country']}",
                f"Descubre las maravillas de {geo_data['name']}.",
                ", ".join(nombres_atracciones[:3]),
                round(random.uniform(800.0, 3000.0), 2)
            )
            cursor.execute(query, datos_destino)
            destinos_agregados += 1
        conn.commit()
        return True, f"{destinos_agregados} destinos sincronizados."
    except requests.exceptions.RequestException as e:
        print(f"Error de red al sincronizar con la API: {e}")
        return False, "Error de red"
    except mysql.connector.Error as e:
        print(f"Error de BD al sincronizar: {e}")
        return False, "Error de BD"
    finally:
        cursor.close()
        conn.close()

# --- API Endpoints para Escritura (Destinos) ---

def create_destino(nombre, descripcion, actividades, costo):
    conn = crear_conexion()
    if not conn: return False
    cursor = conn.cursor()
    try:
        query = "INSERT INTO destinos (nombre, descripcion, actividades, costo) VALUES (%s, %s, %s, %s)" # ID será autoincremental
        cursor.execute(query, (nombre, descripcion, actividades, costo))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error en la API al crear destino: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def update_destino(destino_id, nuevos_datos):
    conn = crear_conexion()
    if not conn: return False
    cursor = conn.cursor()
    try:
        set_clause = ", ".join([f"{key} = %s" for key in nuevos_datos.keys()])
        values = list(nuevos_datos.values())
        values.append(destino_id)
        query = f"UPDATE destinos SET {set_clause} WHERE id = %s"
        cursor.execute(query, tuple(values))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"Error en la API al actualizar destino: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def delete_destino(destino_id):
    conn = crear_conexion()
    if not conn: return False
    cursor = conn.cursor()
    try:
        query = "DELETE FROM destinos WHERE id = %s"
        cursor.execute(query, (destino_id,))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"Error en la API al eliminar destino: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# --- API Endpoints para Escritura (Paquetes) ---

def create_paquete(nombre, fecha_inicio, fecha_fin, cupos, destinos_ids):
    conn = crear_conexion()
    if not conn: return False
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        query_paquete = "INSERT INTO paquetes (nombre, fecha_inicio, fecha_fin, cupos) VALUES (%s, %s, %s, %s)"
        cursor.execute(query_paquete, (nombre, fecha_inicio, fecha_fin, cupos))
        paquete_id = cursor.lastrowid

        query_paquete_destinos = "INSERT INTO paquete_destinos (paquete_id, destino_id) VALUES (%s, %s)"
        destinos_a_insertar = [(paquete_id, dest_id) for dest_id in destinos_ids]
        cursor.executemany(query_paquete_destinos, destinos_a_insertar)

        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error en la API al crear paquete: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def update_paquete_cupos(paquete_id, nuevos_cupos):
    conn = crear_conexion()
    if not conn: return False
    cursor = conn.cursor()
    try:
        query = "UPDATE paquetes SET cupos = %s WHERE id = %s"
        cursor.execute(query, (nuevos_cupos, paquete_id))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"Error en la API al actualizar cupos: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_destinos_for_paquete(paquete_id):
    """Obtiene los destinos asociados a un paquete específico."""
    conn = crear_conexion()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT d.id, d.nombre FROM destinos d
            JOIN paquete_destinos pd ON d.id = pd.destino_id
            WHERE pd.paquete_id = %s
        """
        cursor.execute(query, (paquete_id,))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error en la API al obtener destinos del paquete: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def delete_paquete(paquete_id):
    conn = crear_conexion()
    if not conn: return False
    cursor = conn.cursor()
    try:
        query = "DELETE FROM paquetes WHERE id = %s"
        cursor.execute(query, (paquete_id,))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"Error en la API al eliminar paquete: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def update_paquete_destinos(paquete_id, destinos_ids):
    """Actualiza la lista de destinos para un paquete existente."""
    conn = crear_conexion()
    if not conn: return False
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        # 1. Borrar las relaciones existentes para ese paquete
        cursor.execute("DELETE FROM paquete_destinos WHERE paquete_id = %s", (paquete_id,))
        
        # 2. Insertar las nuevas relaciones
        if destinos_ids: # Solo si la lista no está vacía
            query_insert = "INSERT INTO paquete_destinos (paquete_id, destino_id) VALUES (%s, %s)"
            destinos_a_insertar = [(paquete_id, dest_id) for dest_id in destinos_ids]
            cursor.executemany(query_insert, destinos_a_insertar)
        
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error en la API al actualizar destinos del paquete: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()