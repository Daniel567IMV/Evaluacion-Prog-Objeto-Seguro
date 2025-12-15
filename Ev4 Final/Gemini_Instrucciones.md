# Registro de Cambios y Estructura del Proyecto - Gemini Code Assist

Este archivo resume los componentes desarrollados, los cambios realizados y la estructura final del proyecto para la Agencia de Viajes.

## 1. Estructura General
El proyecto se ha refactorizado para seguir una arquitectura en capas (Model-View-Controller/Service), separando la lógica de base de datos, la lógica de negocio y la interfaz de usuario para hacer el código más ordenado y mantenible.

## 2. Archivos Creados y Modificados

### A. Configuración y Datos
*   **`config.json`**: Archivo creado para almacenar las credenciales de conexión a MySQL de forma separada al código.
*   **`destinos_data.json`**: Archivo JSON que contiene la información semilla de los destinos turísticos.
*   **`Readme.md`**: Documentación general del proyecto, instrucciones de instalación y ejecución.

### B. Base de Datos (`database.py`)
*   **Funcionalidad**: Se implementó la función `inicializar_db_completa()` que automatiza el despliegue:
    1.  Conecta al servidor MySQL (sin seleccionar DB) para crear la base de datos `agencia_viajes` si no existe.
    2.  Crea las tablas necesarias: `usuarios`, `destinos`, `paquetes`, `paquete_destinos`, `reservas`.
    3.  Puebla la tabla `destinos` automáticamente usando `destinos_data.json`.
    4.  Puebla la tabla `paquetes` con datos de prueba (semilla), incluyendo fechas, cupos y costos.

### C. Modelos (`modelos/`)
Definición de objetos Python que representan las tablas de la BD.
*   **`usuario.py`**: Clase Usuario que incluye métodos estáticos para hashing (`hash_password`) y verificación segura de contraseñas.
*   **`destino.py`**: Modelo simple para mapear la tabla de destinos.
*   **`paquete.py`**: Modelo para paquetes turísticos, actualizado para incluir el atributo `costo`.
*   **`reserva.py`**: Actualizado para manejar `destino_id` y `paquete_id`, permitiendo realizar reservas tanto de paquetes completos como de destinos individuales.

### D. Capa de Persistencia (`persistencia/`)
Encargada de ejecutar las consultas SQL directas a la base de datos.
*   **`usuarios_repo.py`**: Métodos para buscar usuarios por username y registrar nuevos usuarios.
*   **`destinos_repo.py`**: Métodos para obtener todos los destinos y buscar por nombre.
*   **`paquetes_repo.py`**: Nuevo repositorio encargado de obtener la lista de paquetes y buscar paquetes por ID desde la base de datos.
*   **`reservas_repo.py`**:
    *   `crear_reserva_paquete`: Maneja transacciones SQL para verificar y restar cupos.
    *   `crear_reserva_destino`: Inserta reservas simples de destinos.
    *   `obtener_reservas_por_usuario`: Realiza `JOINs` SQL para recuperar el historial completo con nombres y costos calculados.

### E. Capa de Servicio (`servicio_negocio/`)
Encargada de la lógica de negocio y validaciones antes de llamar a la persistencia.
*   **`usuario_service.py`**: Valida formatos de correo, longitud de contraseñas y orquesta el login/registro.
*   **`destinos_service.py`**: Intermediario para consultas de destinos.
*   **`paquetes_service.py`**: Contiene la lógica de negocio para los paquetes: valida disponibilidad de cupos, gestiona la transacción de reserva y actualiza el stock de cupos.
*   **`reserva_service.py`**: Valida fechas y cantidades positivas antes de procesar cualquier reserva.
*   **`pais_service.py`**: Conecta con la API RestCountries para obtener información detallada (capital, población, región) y la bandera del país del destino seleccionado.


### F. Interfaz de Usuario (`ui/`)
*   **`tkinter_app.py`**: Aplicación principal de escritorio (Tkinter). Es el archivo responsable de toda la parte visual e interfaz gráfica de la aplicación.
    *   **Login/Registro**: Pantallas funcionales conectadas a la base de datos.
    *   **ClientDashboard**:
        *   Pestaña **Destinos**: Tabla con buscador integrado y formulario de reserva conectado al servicio.
        *   Pestaña **Paquetes**: Nueva sección que lista los paquetes disponibles, muestra sus costos y permite reservarlos validando cupos en tiempo real.
        *   **Integraciones**: Visualización de información del país, banderas, mapas y clima en los paneles de detalle.
        *   Pestaña **Mis Reservas**: Tabla que muestra el historial real del usuario logueado.
    *   **AdminDashboard**: Estructura visual para la gestión de contenidos (backend de gestión parcial).

### G. Ejecución (`app.py`)
*   Script principal ("Entry Point").
*   Llama a `inicializar_db_completa()` al inicio para asegurar que el entorno esté listo antes de mostrar nada.
*   Inicia la aplicación gráfica.

## 3. Resumen de Funcionalidades Agregadas
1.  **Autoinstalación**: La base de datos se crea sola al ejecutar `app.py`.
2.  **Seguridad**: Las contraseñas de los usuarios se guardan encriptadas (SHA-256).
3.  **Reservas Reales**: Los usuarios pueden crear reservas que se guardan en MySQL.
4.  **Historial**: Los usuarios pueden ver sus propias reservas pasadas.
5.  **Buscador**: Filtrado de destinos en tiempo real en la interfaz.
6.  **Gestión de Paquetes**: Implementación completa (Backend y Frontend) para visualizar paquetes con precios y realizar reservas que descuentan cupos automáticamente.
7.  **Integración de APIs Externas**: Se han añadido servicios para Clima, Mapas, Información de Países, Conversión de Moneda y Códigos QR.

## 4. Instrucciones de Uso
1.  Asegúrese de que su servidor MySQL esté corriendo (ej. XAMPP).
2.  Verifique que `config.json` tenga la contraseña correcta de su MySQL local.
3.  Ejecute el comando:
    ```bash
    python app.py
    ```

---