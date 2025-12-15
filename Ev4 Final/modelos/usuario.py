import hashlib

class Usuario:
    """Clase que representa a un usuario (solo datos y hashing)."""
    
    def __init__(self, username, password, nombre=None, apellido=None, correo=None, id=None):
        self.id = id
        self.username = username
        self.password = password  # Contraseña ya hasheada si viene de la DB
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        
    @staticmethod
    def hash_password(password):
        """Genera un hash seguro para la contraseña."""
        # Se asegura de que la entrada sea bytes y usa SHA256.
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_password(hashed_password, provided_password):
        """Compara una contraseña dada con el hash almacenado."""
        return hashed_password == Usuario.hash_password(provided_password)
