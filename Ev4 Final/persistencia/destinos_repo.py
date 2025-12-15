from database import crear_conexion
from modelos.destino import Destino
import mysql.connector

class DestinosRepository:
    def obtener_todos(self):
        """Obtiene todos los destinos de la base de datos."""
        conn = crear_conexion()
        if not conn: return []
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, nombre, descripcion, actividades, costo FROM destinos")
            rows = cursor.fetchall()
            return [Destino(*row) for row in rows]
        except mysql.connector.Error as e:
            print(f"Error al obtener destinos: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def buscar_por_nombre(self, query):
        """Busca destinos cuyo nombre coincida parcialmente con la query."""
        conn = crear_conexion()
        if not conn: return []
        
        cursor = conn.cursor()
        try:
            sql = "SELECT id, nombre, descripcion, actividades, costo FROM destinos WHERE nombre LIKE %s"
            cursor.execute(sql, (f"%{query}%",))
            rows = cursor.fetchall()
            return [Destino(*row) for row in rows]
        except mysql.connector.Error as e:
            print(f"Error al buscar destinos: {e}")
            return []
        finally:
            cursor.close()
            conn.close()