class Paquete:
    def __init__(self, id, nombre, fecha_inicio, fecha_fin, cupos, costo, descripcion=""):
        self.id = id
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.cupos = cupos
        self.costo = costo
        self.descripcion = descripcion