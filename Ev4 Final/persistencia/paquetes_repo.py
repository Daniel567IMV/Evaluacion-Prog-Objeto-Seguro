from database import crear_conexion
from mysql.connector import Error
from modelos.paquete import Paquete

class PaquetesRepository:
    def obtener_todos(self):
        conexion = crear_conexion()
        if not conexion: return []
        cursor = conexion.cursor(dictionary=True)
        lista_paquetes = []
        try:
            cursor.execute("SELECT * FROM paquetes")
            result = cursor.fetchall()
            for row in result:
                lista_paquetes.append(Paquete(
                    row['id'], row['nombre'], row['fecha_inicio'], row['fecha_fin'], row['cupos'], row['costo'], row['descripcion']
                ))
            return lista_paquetes
        except Error as e:
            print(f"Error al obtener paquetes: {e}")
            return []
        finally:
            cursor.close()
            conexion.close()

    def obtener_por_id(self, id):
        conexion = crear_conexion()
        if not conexion: return None
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM paquetes WHERE id = %s", (id,))
            row = cursor.fetchone()
            if row:
                return Paquete(row['id'], row['nombre'], row['fecha_inicio'], row['fecha_fin'], row['cupos'], row['costo'], row['descripcion'])
            return None
        except Error as e:
            print(f"Error al obtener paquete: {e}")
            return None
        finally:
            cursor.close()
            conexion.close()