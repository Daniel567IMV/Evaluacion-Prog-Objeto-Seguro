import tkinter as tk
from database import inicializar_db_completa, crear_conexion
from ui.tkinter_app import App
from persistencia.usuarios_repo import UsuarioRepository
from servicio_negocio.usuario_service import UsuarioService

def asegurar_admin():
    """Crea un usuario administrador por defecto si no existe."""
    conn = crear_conexion()
    if not conn: return
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM usuarios WHERE correo = 'admin@agencia.com'")
        admin = cursor.fetchone()
        
        if not admin:
            print("Creando usuario administrador por defecto...")
            repo = UsuarioRepository()
            service = UsuarioService(repo)
            # Registramos el usuario (por defecto será cliente)
            service.registrar_usuario_nuevo("admin@agencia.com", "admin123", "Admin", "Sistema", "admin@agencia.com")
            # Forzamos el rol a 'admin'
            cursor.execute("UPDATE usuarios SET rol = 'admin' WHERE correo = 'admin@agencia.com'")
            conn.commit()
            print("Admin creado: admin@agencia.com / admin123")
    finally:
        cursor.close()
        conn.close()

def main():
    """
    Punto de entrada principal de la aplicación.
    1. Verifica e inicializa la base de datos MySQL.
    2. Lanza la interfaz gráfica Tkinter.
    """
    print("--- Iniciando Sistema de Agencia de Viajes ---")
    
    # 1. Inicialización de Base de Datos
    print("Verificando e inicializando base de datos...")
    if inicializar_db_completa():
        print("Base de datos lista.")
    else:
        print("ADVERTENCIA: Hubo problemas al inicializar la base de datos. La aplicación podría no funcionar correctamente.")

    # 1.5 Asegurar Admin
    asegurar_admin()

    # 2. Iniciar Interfaz Gráfica
    print("Lanzando interfaz gráfica...")
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()