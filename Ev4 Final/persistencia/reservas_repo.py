# persistencia/reservas_repo.py
from database import crear_conexion
from modelos.reserva import Reserva # Si ya lo movimos
import mysql.connector

class ReservasRepository:
    """Clase dedicada exclusivamente a interactuar con la tabla 'reservas' y 'paquetes' de MySQL."""
    
    def crear_reserva_paquete(self, reserva: Reserva):
        """
        Implementa la lógica de la TRANSACCIÓN para verificar cupos y guardar la reserva.
        """
        conn = crear_conexion()
        if not conn:
            return False, "Error de conexión a la base de datos."
        cursor = conn.cursor()
        
        try:
            conn.start_transaction()
            paquete_id = reserva.paquete_id
            
            # 1. Mirar si quedan plazas (Lógica de Persistencia original)
            cursor.execute("SELECT cupos FROM paquetes WHERE id = %s FOR UPDATE", (paquete_id,))
            cupos_actuales = cursor.fetchone()[0]

            # ⛔ NOTA: La validación de cupos se queda en el Servicio, pero la consulta se hace aquí.
            # En este caso, para simplificar la transacción, mantenemos el SELECT y el UPDATE aquí.
            
            if cupos_actuales < reserva.cantidad_personas:
                conn.rollback()
                # 🛑 Devolvemos un mensaje de error específico para que la Capa de Negocio lo evalúe.
                return False, "No hay suficientes cupos disponibles."

            # 2. Restamos las plazas (UPDATE)
            cursor.execute("UPDATE paquetes SET cupos = cupos - %s WHERE id = %s", 
                           (reserva.cantidad_personas, paquete_id))

            # 3. Guardamos la reserva (INSERT)
            query_reserva = """
                INSERT INTO reservas 
                (usuario_id, destino_id, paquete_id, fecha_reserva, cantidad_personas) 
                VALUES (%s, %s, %s, %s, %s)
            """
            datos = (reserva.usuario_id, reserva.destino_id, reserva.paquete_id, reserva.fecha_reserva, reserva.cantidad_personas)
            cursor.execute(query_reserva, datos)

            conn.commit()
            return True, "Reserva creada exitosamente."
            
        except mysql.connector.Error as e:
            print(f"Error en la transacción de reserva: {e}")
            conn.rollback()
            return False, "Error al procesar la transacción de la reserva."
        finally:
            cursor.close()
            conn.close()

    def crear_reserva_destino(self, reserva: Reserva):
        """Guarda una reserva de un destino individual."""
        conn = crear_conexion()
        if not conn: return False, "Error de conexión."
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO reservas 
                (usuario_id, destino_id, fecha_reserva, cantidad_personas) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (reserva.usuario_id, reserva.destino_id, reserva.fecha_reserva, reserva.cantidad_personas))
            conn.commit()
            return True, "Reserva de destino creada exitosamente."
        except Exception as e:
            print(f"Error al crear reserva de destino: {e}")
            return False, f"Error al guardar reserva: {e}"
        finally:
            cursor.close()
            conn.close()

    def obtener_reservas_por_usuario(self, usuario_id):
        """Obtiene el historial de reservas de un usuario con detalles."""
        conn = crear_conexion()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)
        try:
            # Usamos LEFT JOIN para traer el nombre ya sea de un destino o de un paquete
            query = """
                SELECT r.id, 
                       COALESCE(d.nombre, p.nombre, 'Desconocido') as nombre_item,
                       r.fecha_reserva, 
                       r.cantidad_personas,
                       COALESCE(d.costo * r.cantidad_personas, 0) as costo_total
                FROM reservas r
                LEFT JOIN destinos d ON r.destino_id = d.id
                LEFT JOIN paquetes p ON r.paquete_id = p.id
                WHERE r.usuario_id = %s
                ORDER BY r.fecha_reserva DESC
            """
            cursor.execute(query, (usuario_id,))
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error al obtener historial: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
# Además, mueva las funciones relacionadas con Paquetes y Destinos desde api.py aquí.
