# modelos/reserva.py (Ahora completo)
class Reserva:
    def __init__(self, usuario_id, fecha_reserva, cantidad_personas, paquete_id=None, destino_id=None, id=None):
        self.id = id
        self.usuario_id = usuario_id
        self.paquete_id = paquete_id
        self.destino_id = destino_id
        self.fecha_reserva = fecha_reserva
        self.cantidad_personas = cantidad_personas
        self.fecha_creacion = None  # Se asigna automáticamente en la base de datos