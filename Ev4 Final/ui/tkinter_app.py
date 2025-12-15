import tkinter as tk
from tkinter import ttk, messagebox
import re
import threading

from database import crear_conexion
from persistencia.usuarios_repo import UsuarioRepository
from persistencia.destinos_repo import DestinosRepository
from persistencia.reservas_repo import ReservasRepository
from servicio_negocio.usuario_service import UsuarioService
from servicio_negocio.destinos_service import DestinosService
from servicio_negocio.reserva_service import ReservaService
from servicio_negocio.paquetes_service import PaquetesService
from servicio_negocio.pais_service import PaisService
from modelos.usuario import Usuario

# Inicialización de Servicios
usuario_repo = UsuarioRepository()
destinos_repo = DestinosRepository()
reservas_repo = ReservasRepository()
usuario_service = UsuarioService(repo=usuario_repo)
destinos_service = DestinosService(repo=destinos_repo)
paquetes_service = PaquetesService()
reserva_service = ReservaService(reservas_repository=reservas_repo)
pais_service = PaisService()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agencia de Viajes")
        self.geometry("1200x750")

        style = ttk.Style(self)
        style.theme_use('clam')

        # PALETA DE COLORES "MODERNA Y AMIGABLE"
        PRIMARY_COLOR = "#4A90E2"       # Azul suave y moderno
        SECONDARY_COLOR = "#F5F7FA"     # Fondo casi blanco, muy limpio
        TEXT_COLOR = "#2C3E50"          # Gris oscuro azulado (más elegante)
        BUTTON_HOVER_COLOR = "#357ABD"  # Azul un poco más oscuro para el hover
        TREEVIEW_HEADER_BG = "#DCE4F2"  # Azul grisáceo claro para cabeceras
        WHITE = "#FFFFFF"

        # FUENTES (Segoe UI es estándar en Windows y se ve muy bien)
        MAIN_FONT = ("Segoe UI", 10)
        HEADER_FONT = ("Segoe UI", 20, "bold")
        BUTTON_FONT = ("Segoe UI", 10, "bold")

        self.configure(background=SECONDARY_COLOR)

        style.configure("TFrame", background=SECONDARY_COLOR)
        style.configure("TLabel", background=SECONDARY_COLOR, foreground=TEXT_COLOR, font=MAIN_FONT)
        style.configure("Header.TLabel", font=HEADER_FONT, foreground=PRIMARY_COLOR)
        style.configure("TButton", background=PRIMARY_COLOR, foreground=WHITE, font=BUTTON_FONT, borderwidth=0, padding=8)
        style.map("TButton",
                  background=[('active', BUTTON_HOVER_COLOR)],
                  relief=[('pressed', 'sunken')])
        
        style.configure("Menu.TButton", font=("Segoe UI", 11), padding=(15, 10), relief="flat", background=SECONDARY_COLOR, foreground=TEXT_COLOR, anchor="w")
        style.map("Menu.TButton",
                  background=[('active', PRIMARY_COLOR), ('selected', PRIMARY_COLOR)], foreground=[('active', WHITE), ('selected', WHITE)])
        
        style.configure("TEntry", padding=5, fieldbackground=WHITE)
        style.configure("TLabelframe", background=SECONDARY_COLOR, bordercolor="#BDC3C7", relief="solid", borderwidth=1)
        style.configure("TLabelframe.Label", background=SECONDARY_COLOR, foreground=PRIMARY_COLOR, font=("Segoe UI", 11, "bold"))

        style.configure("Treeview.Heading", background=TREEVIEW_HEADER_BG, foreground=TEXT_COLOR, font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Treeview", rowheight=25, fieldbackground=WHITE, background=WHITE)
        style.map("Treeview.Heading", background=[('active', PRIMARY_COLOR)], foreground=[('active', WHITE)])

        self.current_user = None

        container = ttk.Frame(self, style="TFrame")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginPage, RegisterPage, ClientDashboard, AdminDashboard):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        if hasattr(frame, 'on_show'):
            frame.on_show()
        frame.tkraise()

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="👋 ¡Hola! Inicia Sesión", style="Header.TLabel")
        label.pack(pady=20)

        ttk.Label(self, text="Correo Electrónico:").pack(pady=(10, 2))
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack(pady=5)

        ttk.Label(self, text="Contraseña:").pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        login_button = ttk.Button(self, text="🔐 Entrar", command=self.login)
        login_button.pack(pady=20)

        register_button = ttk.Button(self, text="📝 Crear Cuenta Nueva",
                                     command=lambda: controller.show_frame(RegisterPage))
        register_button.pack()

    def login(self):
        correo = self.username_entry.get()
        password = self.password_entry.get()
        
        usuario, mensaje = usuario_service.autenticar_usuario(correo, password)
        
        if usuario:
            self.controller.current_user = usuario
            
            # Verificar rol (Consulta directa para asegurar)
            conn = crear_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT rol FROM usuarios WHERE id = %s", (usuario.id,))
            res = cursor.fetchone()
            rol = res[0] if res else 'cliente'
            conn.close()

            if rol == 'admin':
                self.controller.show_frame(AdminDashboard)
            else:
                self.controller.show_frame(ClientDashboard)
        else:
            messagebox.showerror("Error", mensaje)

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="✨ Únete a Nosotros", style="Header.TLabel")
        label.pack(pady=20)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10, padx=40)

        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky="w", pady=3)
        self.nombre_entry = ttk.Entry(form_frame, width=30)
        self.nombre_entry.grid(row=0, column=1, pady=2)

        ttk.Label(form_frame, text="Apellido:").grid(row=1, column=0, sticky="w", pady=2)
        self.apellido_entry = ttk.Entry(form_frame, width=30)
        self.apellido_entry.grid(row=1, column=1, pady=2)

        ttk.Label(form_frame, text="Correo Electrónico:").grid(row=2, column=0, sticky="w", pady=2)
        self.correo_entry = ttk.Entry(form_frame, width=30)
        self.correo_entry.grid(row=2, column=1, pady=2)

        ttk.Label(form_frame, text="Contraseña:").grid(row=3, column=0, sticky="w", pady=2)
        self.password_entry = ttk.Entry(form_frame, show="*", width=30)
        self.password_entry.grid(row=3, column=1, pady=2)

        ttk.Label(form_frame, text="Confirmar Contraseña:").grid(row=4, column=0, sticky="w", pady=2)
        self.confirm_password_entry = ttk.Entry(form_frame, show="*", width=30)
        self.confirm_password_entry.grid(row=4, column=1, pady=2)

        register_button = ttk.Button(self, text="✅ Registrarse", command=self.register)
        register_button.pack(pady=20)

        login_button = ttk.Button(self, text="⬅ Volver al Login",
                                  command=lambda: controller.show_frame(LoginPage))
        login_button.pack()

    def validate_password(self, password):
        if len(password) < 4: return False, "La contraseña es muy corta."
        return True, ""

    def validate_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def register(self):
        nombre = self.nombre_entry.get()
        apellido = self.apellido_entry.get()
        correo = self.correo_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not all([nombre, apellido, correo, password, confirm_password]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        
        if not self.validate_email(correo):
            messagebox.showerror("Error de Formato", "El formato del correo electrónico no es válido.")
            return

        if password != confirm_password:
            messagebox.showerror("Error de Contraseña", "Las contraseñas no coinciden.")
            return

        # Llamada corregida al servicio de negocio
        exito, mensaje = usuario_service.registrar_usuario_nuevo(
            username=correo, 
            password_plana=password, 
            nombre=nombre, 
            apellido=apellido, 
            correo=correo
        )
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.controller.show_frame(LoginPage)
        else:
            messagebox.showerror("Error de Registro", mensaje)

class ClientDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=20, pady=10)

        label = ttk.Label(top_frame, text="✈ Tu Panel de Viajes", style="Header.TLabel")
        label.pack(side="left")

        logout_button = ttk.Button(top_frame, text="🚪 Salir", command=self.logout)
        logout_button.pack(side="right")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Tab Destinos ---
        self.tab_destinos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_destinos, text="🌍 Destinos")

        destinos_frame = ttk.LabelFrame(self.tab_destinos, text="🌍 Explora Destinos")
        destinos_frame.pack(pady=10, padx=10, fill="both", expand=True)

        search_frame = ttk.Frame(destinos_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(search_frame, text="Buscar Destino:").pack(side="left", padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(search_frame, text="🔍 Buscar", command=self.buscar_destinos).pack(side="left", padx=5)
        ttk.Button(search_frame, text="📋 Ver Todos", command=self.cargar_destinos).pack(side="left")

        cols = ('ID', 'Nombre', 'Descripción', 'Actividades', 'Costo')
        self.tree_destinos = ttk.Treeview(destinos_frame, columns=cols, show='headings')
        for col in cols:
            self.tree_destinos.heading(col, text=col)
            self.tree_destinos.column(col, width=120)
        self.tree_destinos.pack(expand=True, fill='both', padx=5, pady=5)
        self.tree_destinos.bind("<<TreeviewSelect>>", self.on_destino_select)

        # Un formulario para hacer una reserva del destino que hayamos seleccionado en la tabla.
        reserva_frame = ttk.LabelFrame(self.tab_destinos, text="📅 Planifica tu Viaje")
        reserva_frame.pack(pady=10, padx=10, fill="x")

        # Esta etiqueta nos avisara qué destino tenemos seleccionado.
        ttk.Label(reserva_frame, text="Destino Seleccionado:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.destino_label = ttk.Label(reserva_frame, text="Ninguno", font=("Arial", 10, "italic"))
        self.destino_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(reserva_frame, text="Fecha (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.fecha_entry = ttk.Entry(reserva_frame)
        self.fecha_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(reserva_frame, text="Cantidad de Personas:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.personas_entry = ttk.Entry(reserva_frame)
        self.personas_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.personas_entry.bind("<KeyRelease>", self.actualizar_costo_destino)

        ttk.Label(reserva_frame, text="Costo Total Estimado:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.costo_total_label = ttk.Label(reserva_frame, text="$0", font=("Segoe UI", 10, "bold"), foreground="#E67E22")
        self.costo_total_label.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(reserva_frame, text="✅ Confirmar Reserva", command=self.crear_reserva).grid(row=2, column=2, rowspan=2, padx=20, sticky="ew")

        # --- Panel de Información del País (NUEVO) ---
        self.info_pais_label = ttk.Label(reserva_frame, text="[Info del País]", background="#E1E1E1", relief="sunken", anchor="nw", padding=10, width=30)
        self.info_pais_label.grid(row=0, column=3, rowspan=4, padx=10, pady=5, sticky="ns")

        reserva_frame.columnconfigure(1, weight=1)

        # --- Tab Paquetes ---
        self.tab_paquetes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_paquetes, text="📦 Paquetes")

        paquetes_frame = ttk.LabelFrame(self.tab_paquetes, text="📦 Paquetes Turísticos")
        paquetes_frame.pack(pady=10, padx=10, fill="both", expand=True)

        ttk.Button(paquetes_frame, text="🔄 Actualizar Lista", command=self.cargar_paquetes).pack(anchor="e", padx=5, pady=5)

        # Agregamos 'Descripcion' a las columnas pero la ocultamos con displaycolumns
        cols_p = ('ID', 'Nombre', 'Inicio', 'Fin', 'Cupos', 'Costo', 'Descripcion')
        self.tree_paquetes = ttk.Treeview(paquetes_frame, columns=cols_p, show='headings', displaycolumns=('ID', 'Nombre', 'Inicio', 'Fin', 'Cupos', 'Costo'))

        for col in cols_p:
            if col != 'Descripcion': self.tree_paquetes.heading(col, text=col)
            self.tree_paquetes.column(col, width=100)
        self.tree_paquetes.pack(expand=True, fill='both', padx=5, pady=5)
        self.tree_paquetes.bind("<<TreeviewSelect>>", self.on_paquete_select)

        # Formulario Reserva Paquete
        reserva_p_frame = ttk.LabelFrame(self.tab_paquetes, text="🎫 Reservar Paquete")
        reserva_p_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(reserva_p_frame, text="Paquete Seleccionado:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.paquete_label = ttk.Label(reserva_p_frame, text="Ninguno", font=("Arial", 10, "italic"))
        self.paquete_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(reserva_p_frame, text="Cantidad de Personas:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.personas_p_entry = ttk.Entry(reserva_p_frame)
        self.personas_p_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.personas_p_entry.bind("<KeyRelease>", self.actualizar_costo_paquete)

        ttk.Label(reserva_p_frame, text="Costo Total Estimado:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.costo_total_p_label = ttk.Label(reserva_p_frame, text="$0", font=("Segoe UI", 10, "bold"), foreground="#E67E22")
        self.costo_total_p_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(reserva_p_frame, text="✅ Confirmar Reserva", command=self.crear_reserva_paquete).grid(row=2, column=2, padx=20, sticky="ew")

        # --- Área de Descripción del Paquete ---
        self.paquete_desc_label = ttk.Label(reserva_p_frame, text="Selecciona un paquete para ver detalles.", wraplength=300, justify="left")
        self.paquete_desc_label.grid(row=0, column=3, rowspan=3, padx=10, pady=5, sticky="nw")

        reserva_p_frame.columnconfigure(1, weight=1)
        reserva_p_frame.columnconfigure(3, weight=2)

        # --- Tab Historial ---
        self.tab_historial = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_historial, text="📜 Historial")

        historial_frame = ttk.LabelFrame(self.tab_historial, text="📜 Historial de Viajes")
        historial_frame.pack(pady=10, padx=10, fill="both", expand=True)

        historial_cols = ('ID Reserva', 'Destino', 'Fecha', 'Personas', 'Costo Total')
        self.tree_historial = ttk.Treeview(historial_frame, columns=historial_cols, show='headings')
        for col in historial_cols:
            self.tree_historial.heading(col, text=col)
        self.tree_historial.pack(expand=True, fill='both')

        historial_buttons_frame = ttk.Frame(self.tab_historial)
        historial_buttons_frame.pack(pady=10)
        ttk.Button(historial_buttons_frame, text="🔄 Actualizar", command=self.cargar_historial).pack(side="left", padx=10)
        ttk.Button(historial_buttons_frame, text="❌ Cancelar Reserva", command=self.cancelar_reserva_seleccionada).pack(side="left", padx=10)
        ttk.Button(historial_buttons_frame, text="📂 Exportar CSV", command=self.exportar_historial_csv).pack(side="left", padx=10)

    def on_show(self):
        self.cargar_destinos()
        self.cargar_paquetes()
        self.cargar_historial()

    def cargar_destinos(self):
        for i in self.tree_destinos.get_children():
            self.tree_destinos.delete(i)
        
        destinos = destinos_service.obtener_todos_los_destinos()
        for d in destinos:
            self.tree_destinos.insert('', 'end', values=(d.id, d.nombre, d.descripcion, d.actividades, d.costo))

    def cargar_paquetes(self):
        for i in self.tree_paquetes.get_children():
            self.tree_paquetes.delete(i)
        paquetes = paquetes_service.obtener_todos_los_paquetes()
        for p in paquetes:
            self.tree_paquetes.insert('', 'end', values=(p.id, p.nombre, p.fecha_inicio, p.fecha_fin, p.cupos, f"${p.costo:,.0f}", p.descripcion))

    def buscar_destinos(self):
        query = self.search_entry.get()
        if not query:
            return
        
        for i in self.tree_destinos.get_children():
            self.tree_destinos.delete(i)
            
        destinos = destinos_service.buscar_destinos(query)
        for d in destinos:
            self.tree_destinos.insert('', 'end', values=(d.id, d.nombre, d.descripcion, d.actividades, d.costo))

    def on_destino_select(self, event):
        selected_item = self.tree_destinos.focus()
        if not selected_item: return
        values = self.tree_destinos.item(selected_item, 'values')
        self.destino_label.config(text=f"{values[1]} (ID: {values[0]})")
        
        try:
            self.selected_destino_cost = float(values[4])
        except (ValueError, IndexError):
            self.selected_destino_cost = 0
        self.actualizar_costo_destino()
        
        # Lógica para obtener el país y buscar info
        nombre_completo = values[1] # Ej: "París, Francia"
        if "," in nombre_completo:
            pais = nombre_completo.split(",")[-1].strip()
        else:
            pais = nombre_completo # Caso "Singapur"
            
        self.info_pais_label.config(text="Buscando datos...")
        threading.Thread(target=self.cargar_info_pais_async, args=(pais,), daemon=True).start()

    def cargar_info_pais_async(self, pais):
        exito, info, bandera = pais_service.obtener_info_pais(pais)
        
        def actualizar_ui():
            if exito:
                # compound='bottom' pone la imagen debajo del texto
                self.info_pais_label.config(text=info, image=bandera, compound='bottom')
                self.info_pais_label.image = bandera # Guardar referencia para evitar Garbage Collection
            else:
                self.info_pais_label.config(text=f"No hay datos para:\n{pais}", image='')
        
        self.after(0, actualizar_ui)

    def actualizar_costo_destino(self, event=None):
        if not hasattr(self, 'selected_destino_cost'): return
        try:
            personas = int(self.personas_entry.get())
            total = self.selected_destino_cost * personas
            self.costo_total_label.config(text=f"${total:,.0f}")
        except ValueError:
            self.costo_total_label.config(text="$0")

    def on_paquete_select(self, event):
        selected_item = self.tree_paquetes.focus()
        if not selected_item: return
        values = self.tree_paquetes.item(selected_item, 'values')
        self.paquete_label.config(text=f"{values[1]} (ID: {values[0]})")
        
        try:
            cost_str = str(values[5]).replace('$', '').replace(',', '')
            self.selected_paquete_cost = float(cost_str)
        except (ValueError, IndexError):
            self.selected_paquete_cost = 0
        self.actualizar_costo_paquete()
        
        # Mostrar descripción
        descripcion = values[6] # Índice 6 es la descripción
        self.paquete_desc_label.config(text=descripcion)

    def actualizar_costo_paquete(self, event=None):
        if not hasattr(self, 'selected_paquete_cost'): return
        try:
            personas = int(self.personas_p_entry.get())
            total = self.selected_paquete_cost * personas
            self.costo_total_p_label.config(text=f"${total:,.0f}")
        except ValueError:
            self.costo_total_p_label.config(text="$0")

    def crear_reserva(self):
        # 1. Obtener datos de la UI
        selected_item = self.tree_destinos.focus()
        if not selected_item:
            messagebox.showwarning("Atención", "Por favor, selecciona un destino de la lista.")
            return

        values = self.tree_destinos.item(selected_item, 'values')
        destino_id = values[0]
        fecha = self.fecha_entry.get()
        personas = self.personas_entry.get()
        usuario_id = self.controller.current_user.id

        # 2. Llamar al servicio
        exito, mensaje = reserva_service.procesar_reserva_destino(usuario_id, destino_id, fecha, personas)

        if exito:
            messagebox.showinfo("Éxito", mensaje)
            # Opcional: Limpiar campos
            self.fecha_entry.delete(0, tk.END)
            self.personas_entry.delete(0, tk.END)
            self.costo_total_label.config(text="$0")
        else:
            messagebox.showerror("Error", mensaje)

    def crear_reserva_paquete(self):
        selected_item = self.tree_paquetes.focus()
        if not selected_item:
            messagebox.showwarning("Atención", "Por favor, selecciona un paquete de la lista.")
            return

        values = self.tree_paquetes.item(selected_item, 'values')
        paquete_id = values[0]
        personas = self.personas_p_entry.get()
        usuario_id = self.controller.current_user.id

        exito, mensaje = paquetes_service.procesar_reserva_paquete(usuario_id, paquete_id, personas)
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.personas_p_entry.delete(0, tk.END)
            self.costo_total_p_label.config(text="$0")
            self.cargar_paquetes() # Recargar para ver cupos actualizados
        else:
            messagebox.showerror("Error", mensaje)

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame(LoginPage)

    def cargar_historial(self):
        """Carga las reservas del usuario actual en la tabla."""
        # Limpiar tabla actual
        for i in self.tree_historial.get_children():
            self.tree_historial.delete(i)
            
        if not self.controller.current_user:
            return

        usuario_id = self.controller.current_user.id
        reservas = reserva_service.obtener_historial(usuario_id)
        
        # Obtener datos para recálculo de costos (Fix para costo 0)
        all_destinos = destinos_service.obtener_todos_los_destinos()
        all_paquetes = paquetes_service.obtener_todos_los_paquetes()
        
        # Mapeos para búsqueda rápida
        destinos_map = {d.id: d.costo for d in all_destinos}
        paquetes_map = {p.id: p.costo for p in all_paquetes}
        # Fallback por nombre
        destinos_name_map = {d.nombre: d.costo for d in all_destinos}
        paquetes_name_map = {p.nombre: p.costo for p in all_paquetes}

        for r in reservas:
            costo_final = r.get('costo_total') or 0
            
            # Lógica de corrección si el costo es 0
            if costo_final == 0:
                cantidad = r.get('cantidad_personas', 0)
                costo_unitario = 0
                
                # 1. Intentar por ID
                if r.get('destino_id') in destinos_map:
                    costo_unitario = destinos_map[r['destino_id']]
                elif r.get('paquete_id') in paquetes_map:
                    costo_unitario = paquetes_map[r['paquete_id']]
                
                # 2. Intentar por Nombre (si ID falló)
                if costo_unitario == 0:
                    nombre = r.get('nombre_item')
                    if nombre in destinos_name_map:
                        costo_unitario = destinos_name_map[nombre]
                    elif nombre in paquetes_name_map:
                        costo_unitario = paquetes_name_map[nombre]
                
                costo_final = costo_unitario * cantidad

            # Insertamos los datos obtenidos del repositorio
            self.tree_historial.insert('', 'end', values=(r['id'], r['nombre_item'], r['fecha_reserva'], r['cantidad_personas'], f"${costo_final:,.0f}"))

    def cancelar_reserva_seleccionada(self):
        # Pendiente de implementación
        messagebox.showinfo("Info", "Funcionalidad de cancelar reserva en desarrollo.")

    def exportar_historial_csv(self):
        # Pendiente de implementación
        messagebox.showinfo("Info", "Funcionalidad de exportar a CSV en desarrollo.")

class AdminDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(header_frame, text="🛠 Panel de Administrador", style="Header.TLabel").pack(side="left")
        ttk.Button(header_frame, text="🚪 Salir", command=self.logout).pack(side="right")

        # Content
        content_frame = ttk.LabelFrame(self, text="Gestión de Reservas Globales")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Toolbar
        toolbar = ttk.Frame(content_frame)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(toolbar, text="🔄 Actualizar Lista", command=self.cargar_reservas).pack(side="left", padx=5)
        ttk.Button(toolbar, text="✏ Editar Seleccionada", command=self.editar_reserva).pack(side="left", padx=5)
        ttk.Button(toolbar, text="❌ Eliminar Seleccionada", command=self.eliminar_reserva).pack(side="left", padx=5)

        # Buscador por correo
        ttk.Label(toolbar, text="|").pack(side="left", padx=10)
        self.search_entry = ttk.Entry(toolbar, width=25)
        self.search_entry.pack(side="left", padx=5)
        ttk.Button(toolbar, text="🔍 Buscar por Correo", command=self.buscar_reservas).pack(side="left", padx=5)
        
        # Treeview
        cols = ('ID', 'Usuario', 'Item', 'Tipo', 'Fecha', 'Pax', 'Creada')
        self.tree = ttk.Treeview(content_frame, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.column('Usuario', width=150)
        self.tree.column('Item', width=200)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

    def on_show(self):
        self.cargar_reservas()

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame(LoginPage)

    def buscar_reservas(self):
        termino = self.search_entry.get()
        self.cargar_reservas(filtro_correo=termino)

    def cargar_reservas(self, filtro_correo=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        conn = crear_conexion()
        if not conn: return
        cursor = conn.cursor()
        try:
            query = """
                SELECT r.id, u.correo, 
                       COALESCE(d.nombre, p.nombre) as item,
                       CASE WHEN r.destino_id IS NOT NULL THEN 'Destino' ELSE 'Paquete' END as tipo,
                       r.fecha_reserva, r.cantidad_personas, r.fecha_creacion
                FROM reservas r
                JOIN usuarios u ON r.usuario_id = u.id
                LEFT JOIN destinos d ON r.destino_id = d.id
                LEFT JOIN paquetes p ON r.paquete_id = p.id
            """
            
            if filtro_correo:
                query += " WHERE u.correo LIKE %s"
                params = (f"%{filtro_correo}%",)
            else:
                params = ()
            
            query += " ORDER BY r.id DESC"
            
            cursor.execute(query, params)
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las reservas: {e}")
        finally:
            cursor.close()
            conn.close()

    def eliminar_reserva(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona una reserva para eliminar.")
            return
        
        reserva_id = self.tree.item(selected, 'values')[0]
        confirm = messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar la reserva ID {reserva_id}?\nEsta acción es irreversible.")
        
        if confirm:
            conn = crear_conexion()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM reservas WHERE id = %s", (reserva_id,))
                conn.commit()
                messagebox.showinfo("Éxito", "Reserva eliminada.")
                self.cargar_reservas()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {e}")
            finally:
                cursor.close()
                conn.close()

    def editar_reserva(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona una reserva para editar.")
            return
            
        values = self.tree.item(selected, 'values')
        reserva_id = values[0]
        current_pax = values[5]
        
        # Ventana emergente simple
        edit_win = tk.Toplevel(self)
        edit_win.title(f"Editar Reserva {reserva_id}")
        edit_win.geometry("300x150")
        
        ttk.Label(edit_win, text="Nueva Cantidad de Personas:").pack(pady=10)
        pax_entry = ttk.Entry(edit_win)
        pax_entry.insert(0, current_pax)
        pax_entry.pack(pady=5)
        
        def guardar_cambios():
            nuevo_pax = pax_entry.get()
            if not nuevo_pax.isdigit() or int(nuevo_pax) < 1:
                messagebox.showerror("Error", "Ingresa un número válido.")
                return
                
            conn = crear_conexion()
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE reservas SET cantidad_personas = %s WHERE id = %s", (nuevo_pax, reserva_id))
                conn.commit()
                messagebox.showinfo("Éxito", "Reserva actualizada.")
                edit_win.destroy()
                self.cargar_reservas()
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar: {e}")
            finally:
                cursor.close()
                conn.close()
                
        ttk.Button(edit_win, text="Guardar", command=guardar_cambios).pack(pady=10)