# Sistema de Gestión de Agencia de Viajes

Aplicación de escritorio desarrollada en Python para la gestión integral de una agencia de viajes. Permite a los clientes explorar destinos, reservar paquetes y gestionar su historial, mientras que los administradores pueden gestionar el catálogo de ofertas.

## Características Principales

*   **Gestión de Usuarios**: Registro y autenticación segura (hashing de contraseñas).
*   **Catálogo de Destinos**: Búsqueda y visualización de destinos turísticos con detalles y costos.
*   **Paquetes Turísticos**: Gestión de paquetes que agrupan múltiples destinos con control de cupos.
*   **Reservas**: Funcionalidad para que los usuarios reserven destinos o paquetes.
*   **Historial**: Visualización de reservas realizadas por el usuario.
*   **Panel de Administración**: Interfaz para crear, editar y eliminar destinos y paquetes.
*   **Base de Datos**: Persistencia robusta utilizando MySQL.

## Requisitos del Sistema

*   Python 3.8 o superior.
*   Servidor MySQL (local o remoto).

## Instalación y Configuración

1.  **Instalar Dependencias**
    Ejecuta el siguiente comando para instalar las librerías necesarias:
    ```bash
    pip install mysql-connector-python streamlit
    ```
    *(Nota: `tkinter` generalmente viene incluido con la instalación estándar de Python).*

2.  **Configurar la Base de Datos**
    Crea un archivo llamado `config.json` en la carpeta raíz del proyecto con tus credenciales de MySQL:

    ```json
    {
        "MYSQL_CONFIG": {
            "host": "localhost",
            "user": "root",
            "password": "tu_contraseña_aqui",
            "database": "agencia_viajes"
        },
        "OPENTRIPMAP_API_KEY": "TU_API_KEY_OPCIONAL"
    }
    ```

3.  **Datos Iniciales**
    Asegúrate de que el archivo `destinos_data.json` esté en la raíz del proyecto. La aplicación lo usará para poblar la base de datos la primera vez que se ejecute.

## Ejecución

Para iniciar la aplicación principal (Interfaz de Escritorio):

```bash
python app.py
```

*Al ejecutar este comando, el sistema verificará automáticamente la conexión a la base de datos, creará las tablas si no existen y cargará los datos de ejemplo.*

## Estructura del Proyecto

*   `app.py`: Lanzador principal de la aplicación.
*   `database.py`: Módulo de conexión e inicialización de la base de datos.
*   `ui/`: Contiene las interfaces gráficas (`tkinter_app.py` y `streamlit_app.py`).
*   `modelos/`: Definición de clases (Usuario, Destino, Paquete, Reserva).
*   `persistencia/`: Repositorios para el acceso a datos (SQL).
*   `servicio_negocio/`: Lógica de negocio y validaciones.

---
Desarrollado para el prototipo de Agencia de Viajes - Avance ev4.