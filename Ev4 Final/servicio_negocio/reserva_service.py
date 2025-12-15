# servicio_negocio/reserva_service.py
from datetime import date
from persistencia.reservas_repo import ReservasRepository
from modelos.reserva import Reserva

class ReservaService:
    def __init__(self, reservas_repository: ReservasRepository):
        # 🔑 Inyección de Dependencias: El servicio necesita un Repositorio para funcionar.
        self.repo = reservas_repository

    def procesar_nueva_reserva(self, usuario_id, paquete_id, fecha_str, cantidad_personas_str):
        # 1. Validación de Reglas de Negocio (Aquí irían validaciones complejas)
        
        # Validación simple de fecha y cantidad (se puede mover aquí o dejar en la UI, pero mejor aquí)
        try:
            cantidad_personas = int(cantidad_personas_str)
        except ValueError:
            return False, "La cantidad de personas debe ser un número entero."
        
        if cantidad_personas <= 0:
            return False, "La cantidad de personas debe ser positiva."

        # Validación de fecha (ejemplo)
        # if date.fromisoformat(fecha_str) < date.today():
        #     return False, "No se puede reservar en una fecha pasada."
        
        # 2. Crear el Modelo (Datos limpios)
        reserva = Reserva(
            usuario_id=usuario_id, 
            paquete_id=paquete_id, 
            fecha_reserva=fecha_str, # Nota: Idealmente se pasa como objeto datetime
            cantidad_personas=cantidad_personas
        )

        # 3. Delegar la persistencia al Repositorio
        # El Servicio NO sabe que hay un SELECT, un UPDATE o un COMMIT; solo pide "crear".
        exito, mensaje = self.repo.crear_reserva_paquete(reserva)
        
        return exito, mensaje

    def procesar_reserva_destino(self, usuario_id, destino_id, fecha_str, cantidad_personas_str):
        """Procesa la reserva de un destino individual."""
        try:
            cantidad = int(cantidad_personas_str)
            if cantidad <= 0: return False, "La cantidad debe ser mayor a 0."
        except ValueError:
            return False, "Cantidad inválida."

        if not fecha_str: return False, "La fecha es obligatoria."

        reserva = Reserva(
            usuario_id=usuario_id,
            destino_id=destino_id,
            fecha_reserva=fecha_str,
            cantidad_personas=cantidad
        )
        
        return self.repo.crear_reserva_destino(reserva)

    def obtener_historial(self, usuario_id):
        """Devuelve la lista de reservas de un usuario."""
        return self.repo.obtener_reservas_por_usuario(usuario_id)
