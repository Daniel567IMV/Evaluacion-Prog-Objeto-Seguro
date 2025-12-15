# servicio_negocio/usuario_service.py
from persistencia.usuarios_repo import UsuarioRepository
from modelos.usuario import Usuario
import re # Para las validaciones de negocio (ej. email)

class UsuarioService:
    def __init__(self, repo: UsuarioRepository):
        # 🔑 Inyección de Dependencias
        self.repo = repo
    
    # --- Lógica de Negocio (Login) ---
    def autenticar_usuario(self, username, password_plana):
        """
        Busca el usuario y verifica la contraseña. 
        Retorna el objeto Usuario si es exitoso, None en caso contrario.
        """
        usuario_db = self.repo.obtener_usuario_por_username(username)
        
        if not usuario_db:
            return None, "Usuario no encontrado."
            
        # El servicio usa el Modelo para verificar la lógica intrínseca (hashing)
        if Usuario.verify_password(usuario_db.password, password_plana):
            return usuario_db, "Autenticación exitosa."
        else:
            return None, "Contraseña incorrecta."

    # --- Lógica de Negocio (Registro) ---
    def registrar_usuario_nuevo(self, username, password_plana, nombre, apellido, correo):
        """
        Aplica validaciones, hashea la contraseña y delega el guardado al Repositorio.
        """
        # 1. Validaciones de Negocio
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            return False, "Formato de correo inválido."
        if len(password_plana) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres."
        
        # 2. Creación del Modelo con Contraseña Hasheada
        hashed_password = Usuario.hash_password(password_plana)
        
        nuevo_usuario = Usuario(
            username=username,
            password=hashed_password, # El modelo ya lleva el hash
            nombre=nombre,
            apellido=apellido,
            correo=correo
        )
        
        # 3. Delegar la Persistencia al Repositorio
        return self.repo.registrar_nuevo_usuario(nuevo_usuario)
