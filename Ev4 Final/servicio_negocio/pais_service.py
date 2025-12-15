import requests
from io import BytesIO
from PIL import Image, ImageTk

class PaisService:
    def __init__(self):
        # API pública y gratuita V3.1
        self.base_url = "https://restcountries.com/v3.1/name"
        # Agregamos User-Agent para evitar bloqueos por parte de la API
        self.headers = {
            'User-Agent': 'AgenciaViajesPrototipo/1.0'
        }

    def obtener_info_pais(self, nombre_pais):
        """
        Busca información detallada de un país.
        Retorna: (Exito, Texto_Info, Imagen_Bandera_Tk)
        """
        # Mapeo para corregir nombres que la API podría no entender en español abreviado
        correcciones = {
            "EE.UU.": "USA",
            "EAU": "United Arab Emirates",
            "Reino Unido": "United Kingdom",
            "Corea del Sur": "South Korea",
            "Rusia": "Russia",
            "Holanda": "Netherlands",
            "Países Bajos": "Netherlands",
            "México": "Mexico",
            "Perú": "Peru",
            "Japón": "Japan",
            "Francia": "France",
            "Italia": "Italy",
            "España": "Spain",
            "Alemania": "Germany",
            "Brasil": "Brazil",
            "Egipto": "Egypt",
            "Tailandia": "Thailand",
            "Turquía": "Turkey",
            "Grecia": "Greece",
            "República Checa": "Czech Republic",
            "Singapur": "Singapore",
            "Austria": "Austria",
            "Portugal": "Portugal",
            "Irlanda": "Ireland",
            "Escocia": "United Kingdom", # Escocia es parte de UK en esta API
            "China": "China",
            "Vietnam": "Vietnam",
            "Camboya": "Cambodia",
            "Indonesia": "Indonesia",
            "Marruecos": "Morocco",
            "Sudáfrica": "South Africa",
            "Tanzania": "Tanzania",
            "Zambia/Zimbabue": "Zimbabwe", # Elegimos uno de los dos para que la API responda
            "Islandia": "Iceland",
            "Canadá": "Canada",
            "Panamá": "Panama",
            "Nueva Zelanda": "New Zealand",
            "Hungría": "Hungary",
            "Polonia": "Poland",
            "Suiza": "Switzerland",
            "Dinamarca": "Denmark",
            "Suecia": "Sweden",
            "Noruega": "Norway",
            "Finlandia": "Finland",
            "República Dominicana": "Dominican Republic",
            "Kenia": "Kenya",
            "Bélgica": "Belgium",
            "Croacia": "Croatia",
            "Jordania": "Jordan"
        }
        
        busqueda = correcciones.get(nombre_pais, nombre_pais)

        try:
            # fullText=false para permitir búsquedas parciales si es necesario
            url = f"{self.base_url}/{busqueda}"
            # Aumentamos el timeout y agregamos headers para mayor estabilidad
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data_list = response.json()
                
                # Intentamos buscar la coincidencia más exacta para evitar errores (ej. India vs British Indian Ocean Territory)
                data = data_list[0] # Por defecto tomamos el primero
                for p in data_list:
                    # Verificamos nombre común en inglés
                    if p.get('name', {}).get('common', '').lower() == busqueda.lower():
                        data = p
                        break
                    # Verificamos traducción en español
                    if p.get('translations', {}).get('spa', {}).get('common', '').lower() == nombre_pais.lower():
                        data = p
                        break
                
                nombre_oficial = data.get('name', {}).get('common', nombre_pais)
                capital = data.get('capital', ['N/A'])[0]
                poblacion = data.get('population', 0)
                region = data.get('region', 'N/A')
                
                # --- Obtener Bandera ---
                bandera_tk = None
                flag_url = data.get('flags', {}).get('png')
                if flag_url:
                    try:
                        img_resp = requests.get(flag_url, headers=self.headers, timeout=5)
                        if img_resp.status_code == 200:
                            img_data = BytesIO(img_resp.content)
                            pil_img = Image.open(img_data)
                            # Redimensionamos para que no sea gigante (ancho 150px)
                            base_width = 150
                            w_percent = (base_width / float(pil_img.size[0]))
                            h_size = int((float(pil_img.size[1]) * float(w_percent)))
                            pil_img = pil_img.resize((base_width, h_size), Image.Resampling.LANCZOS)
                            bandera_tk = ImageTk.PhotoImage(pil_img)
                    except Exception:
                        pass # Si falla la imagen, no rompemos el flujo, solo no se muestra

                # Formateamos el texto para mostrarlo en la app
                info = (
                    f"País: {nombre_oficial}\n"
                    f"Capital: {capital}\n"
                    f"Región: {region}\n"
                    f"Población: {poblacion:,.0f} habs."
                )
                return True, info, bandera_tk
            else:
                print(f"Error API Países: {response.status_code} para {busqueda}")
                return False, "Información no disponible.", None
        except Exception as e:
            print(f"Excepción API Países: {e}")
            return False, "Error de conexión.", None