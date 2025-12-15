# persistencia/usuarios_repo.py
from database import crear_conexion
from modelos.usuario import Usuario
import mysql.connector

class UsuarioRepository:
    """Maneja las operaciones CRUD de la tabla 'usuarios' de MySQL."""

    def obtener_usuario_por_username(self, username):
        """Busca y retorna un objeto Usuario por nombre de usuario."""
        conn = crear_conexion()
        if not conn: return None
        cursor = conn.cursor(dictionary=True) # dictionary=True permite obtener resultados como dict
        
        try:
            query = "SELECT id, username, password_hash, nombre, apellido, correo FROM usuarios WHERE username = %s"
            cursor.execute(query, (username,))
            data = cursor.fetchone()
            
            if data:
                # Retorna un objeto modelo Usuario
                return Usuario(
                    id=data['id'],
                    username=data['username'],
                    password=data['password_hash'], # Esto es el hash
                    nombre=data['nombre'],
                    apellido=data['apellido'],
                    correo=data['correo']
                )
            return None
        except mysql.connector.Error as e:
            print(f"Error en el repositorio al obtener usuario: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def registrar_nuevo_usuario(self, usuario: Usuario):
        """Inserta un nuevo usuario en la base de datos."""
        conn = crear_conexion()
        if not conn: return False, "Error de conexión a la base de datos."
        cursor = conn.cursor()
        
        try:
            # 1. Verificar si el usuario ya existe (Regla de unicidad)
            if self.obtener_usuario_por_username(usuario.username):
                return False, "El nombre de usuario ya está registrado."
            
            # 2. Insertar el nuevo usuario
            query = """
                INSERT INTO usuarios (username, password_hash, nombre, apellido, correo) 
                VALUES (%s, %s, %s, %s, %s)
            """
            # El hash ya debe venir listo desde la Capa de Servicio
            datos = (usuario.username, usuario.password, usuario.nombre, usuario.apellido, usuario.correo)
            cursor.execute(query, datos)
            conn.commit()
            return True, "Registro exitoso."
            
        except mysql.connector.Error as e:
            print(f"Error en el repositorio al registrar usuario: {e}")
            conn.rollback()
            return False, f"Error de BD al registrar: {e}"
        finally:
            cursor.close()
            conn.close()
