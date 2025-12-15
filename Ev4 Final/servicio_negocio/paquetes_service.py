from persistencia.paquetes_repo import PaquetesRepository
from database import crear_conexion
from mysql.connector import Error

class PaquetesService:
    def __init__(self, repo=None):
        self.repo = repo or PaquetesRepository()

    def obtener_todos_los_paquetes(self):
        return self.repo.obtener_todos()

    def procesar_reserva_paquete(self, usuario_id, paquete_id, cantidad_personas):
        if not paquete_id or not cantidad_personas:
            return False, "Datos incompletos."
        
        try:
            cantidad = int(cantidad_personas)
            if cantidad <= 0: return False, "La cantidad de personas debe ser positiva."
        except ValueError:
            return False, "Cantidad de personas inválida."

        paquete = self.repo.obtener_por_id(paquete_id)
        if not paquete:
            return False, "Paquete no encontrado."
            
        if paquete.cupos < cantidad:
            return False, "No hay suficientes cupos disponibles."

        conexion = crear_conexion()
        if not conexion: return False, "Error de conexión."
        
        cursor = conexion.cursor()
        try:
            # Usamos la fecha de inicio del paquete como fecha de reserva
            fecha_reserva = paquete.fecha_inicio
            
            query_reserva = "INSERT INTO reservas (usuario_id, paquete_id, fecha_reserva, cantidad_personas) VALUES (%s, %s, %s, %s)"
            cursor.execute(query_reserva, (usuario_id, paquete_id, fecha_reserva, cantidad))
            
            query_cupos = "UPDATE paquetes SET cupos = cupos - %s WHERE id = %s"
            cursor.execute(query_cupos, (cantidad, paquete_id))
            
            conexion.commit()
            return True, f"Reserva del paquete '{paquete.nombre}' realizada con éxito."
        except Error as e:
            conexion.rollback()
            return False, f"Error al procesar reserva: {e}"
        finally:
            cursor.close()
            conexion.close()