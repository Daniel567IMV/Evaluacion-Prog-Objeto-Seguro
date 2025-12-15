from persistencia.destinos_repo import DestinosRepository

class DestinosService:
    def __init__(self, repo: DestinosRepository):
        self.repo = repo

    def obtener_todos_los_destinos(self):
        return self.repo.obtener_todos()

    def buscar_destinos(self, query):
        return self.repo.buscar_por_nombre(query)