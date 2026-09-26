import streamlit as st
import base64
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Valeria & Hector | Padrinos de Boda",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# DATOS FIJOS DE LA BODA
# =========================================================

NOVIOS = "Valeria & Hector"
FECHA_DIA = "08"
FECHA_MES = "ENERO · 2027"
HORA = "05:00 PM"

LUGAR = "Parroquia Nuestra Señora del Café"
CIUDAD = "Armenia, Quindío"

FORMS_URL = "https://forms.gle/4cGepJCuvvtpjZpq6"

MENSAJE = """
Estamos por unir nuestras vidas y hay un lugar muy importante
que queremos que ocupes ese día: el de <strong>padrino / madrina</strong>
de nuestra boda.
"""

CUERPO = """
Tu cariño y tu presencia han sido parte de nuestro camino,
y nos encantaría contar contigo para acompañarnos
también frente al altar.
"""

# Saludo por defecto si no se identifica al invitado por la URL
SALUDO_GENERICO = "Querid@ amig@"

# Lista opcional de invitados: código (va en el enlace) -> nombre que se muestra
# Si tu invitado no está en la lista, se usa el SALUDO_GENERICO.
INVITADOS = {
    "maria-jose": "Maria Jose",
    "sandra-liliana": "Sandra Liliana",
    "hector-fabio": "Hector Fabio",
    "liliana": "Liliana",
    "valeria-ramos": "Valeria Ramos",
    "hector-salazar": "Hector Salazar",
}


# =========================================================
# PALETA
# =========================================================

BLANCO = "#FFFDFC"
BEIGE = "#F2EBDD"
OLIVA = "#667052"
TERRACOTA = "#B96F57"
CARBON = "#30352C"


# =========================================================
# FOTO DE FONDO: CONFIGURACIÓN
# =========================================================

# True  -> muestra el panel lateral para subir la foto de portada.
# False -> versión final para los invitados (sin panel).
MODO_EDICION = True

# Foto definitiva (la que verán los invitados) si ya tienes el archivo
# guardado junto a este script. Escribe aquí su nombre, por ejemplo:
# FOTO_PORTADA_FIJA = "portada.jpg"
FOTO_PORTADA_FIJA = None

# Carpetas donde se busca la foto de portada (junto a este archivo).
NOMBRES_CARPETA_FOTOS = ("fotos", "mi-carpeta")
EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp"}

# Velo oscuro sobre la foto para que el texto blanco siga leyéndose.
# El contraste real lo da el panel translúcido detrás del texto
# (clase .hero-content en el CSS), así que este degradado puede
# ser más suave.
HERO_DEGRADADO = "linear-gradient(180deg, rgba(15,16,12,0.45) 0%, rgba(15,16,12,0.55) 100%)"


# =========================================================
# FUNCIONES DE FOTO
# =========================================================

def html_block(codigo):
    """Muestra HTML en Streamlit, sin dejar que Markdown lo interprete."""
    limpio = "\n".join(
        linea.strip() for linea in codigo.splitlines() if linea.strip()
    )
    st.markdown(limpio, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def optimizar(datos, max_lado=1800, calidad=82):
    """Reduce el tamaño de la foto para que la invitación cargue rápido."""
    img = Image.open(BytesIO(datos))
    img = ImageOps.exif_transpose(img)  # respeta la rotación del celular
    img.thumbnail((max_lado, max_lado))

    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        fondo = Image.new("RGB", img.size, (255, 253, 252))
        fondo.paste(img, mask=img.split()[-1])
        img = fondo
    else:
        img = img.convert("RGB")

    salida = BytesIO()
    img.save(salida, "JPEG", quality=calidad, optimize=True)
    return salida.getvalue()


def a_data_uri(datos, max_lado=1800):
    b64 = base64.b64encode(optimizar(datos, max_lado)).decode()
    return f"data:image/jpeg;base64,{b64}"


def carpetas_de_fotos():
    """Carpetas existentes donde buscar la foto (junto a este script)."""
    bases = [Path(__file__).resolve().parent, Path.cwd()]
    encontradas = []

    for base in bases:
        for nombre in NOMBRES_CARPETA_FOTOS:
            carpeta = base / nombre
            if carpeta.is_dir() and carpeta not in encontradas:
                encontradas.append(carpeta)

    return encontradas


def buscar_foto_fija():
    """Busca FOTO_PORTADA_FIJA en las carpetas del repositorio."""
    if not FOTO_PORTADA_FIJA:
        return None

    for carpeta in carpetas_de_fotos():
        ruta = carpeta / FOTO_PORTADA_FIJA
        if ruta.is_file():
            return ruta.read_bytes()

    # también revisa junto al propio script
    ruta = Path(__file__).resolve().parent / FOTO_PORTADA_FIJA
    if ruta.is_file():
        return ruta.read_bytes()

    return None


def estilo_hero(datos, posicion):
    """Devuelve el atributo style de la portada (con o sin foto)."""
    if not datos:
        return ""

    uri = a_data_uri(datos)

    return (
        f'style="background-image: {HERO_DEGRADADO}, url(\'{uri}\'); '
        f'background-size: cover; '
        f'background-position: center {posicion}%;"'
    )


# =========================================================
# INVITADO (personalización por enlace)
# =========================================================

parametros = st.query_params
codigo_invitado = parametros.get("invitado", "")
nombre_invitado = INVITADOS.get(codigo_invitado, SALUDO_GENERICO)


# =========================================================
# PANEL DE CONFIGURACIÓN (solo con MODO_EDICION = True)
# =========================================================

foto_portada = buscar_foto_fija()
posicion_portada = 50

if MODO_EDICION:

    with st.sidebar:

        st.markdown("## 🌿 Configuración")
        st.markdown("### Invitación de padrinos")
        st.caption("Este panel se oculta al poner MODO_EDICION = False.")

        st.divider()

        subida = st.file_uploader(
            "Foto de fondo de la portada",
            type=["jpg", "jpeg", "png", "webp"]
        )

        if subida is not None:
            foto_portada = subida.getvalue()

        if foto_portada:
            posicion_portada = st.slider(
                "Encuadre vertical de la foto",
                0, 100, 50,
                help="0 = se ve la parte de arriba de la foto, 100 = la de abajo."
            )
        else:
            st.info(
                "Sin foto, la portada se ve con el color oliva de fondo. "
                "Sube una foto arriba, o guarda tu imagen junto a este "
                f"script con el nombre que pongas en FOTO_PORTADA_FIJA."
            )

        st.divider()

        st.markdown("### 🔗 Probar un enlace de invitado")
        st.code(
            f"https://TU-DOMINIO.streamlit.app/?invitado=maria-jose"
        )
        st.caption(
            "Cambia el código al final por cualquiera de la lista "
            "INVITADOS en el código."
        )


# =========================================================
# ESTILOS
# =========================================================

html_block(
    f"""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Montserrat:wght@400;500;600&display=swap');

    .stApp {{
        background: {BEIGE};
    }}

    #MainMenu, header, footer {{ visibility: hidden; }}

    .block-container {{
        padding: 0 !important;
        max-width: 640px !important;
        margin: 0 auto !important;
    }}

    section {{
        padding: 90px 24px;
        text-align: center;
    }}

    .hero {{
        background: {OLIVA};
        color: {BLANCO};
        min-height: 92vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px 24px;
    }}

    .hero-content {{
        background: rgba(15,16,12,0.42);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 20px;
        padding: 44px 36px;
        max-width: 440px;
    }}

    .eyebrow {{
        font-family: 'Montserrat', sans-serif;
        font-size: 13px;
        letter-spacing: 3px;
        opacity: 0.95;
    }}

    .names {{
        font-family: 'Cormorant Garamond', serif;
        font-weight: 600;
        font-size: 74px;
        line-height: 1.05;
        margin: 22px 0 10px 0;
    }}

    .names em {{
        font-style: italic;
        color: #E3A08C;
    }}

    .subtitle {{
        font-family: 'Cormorant Garamond', serif;
        font-size: 26px;
        font-style: italic;
        max-width: 380px;
        margin: 6px auto 0 auto;
    }}

    .branch {{
        font-size: 26px;
        margin-top: 34px;
        opacity: 0.95;
    }}

    .section-beige {{ background: {BEIGE}; }}
    .section-white {{ background: {BLANCO}; }}

    .section-label {{
        font-family: 'Montserrat', sans-serif;
        font-size: 13px;
        letter-spacing: 3px;
        color: {TERRACOTA};
        margin-bottom: 18px;
    }}

    .guest-name {{
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 34px;
        color: {OLIVA};
        margin-bottom: 8px;
    }}

    .message {{
        font-family: 'Cormorant Garamond', serif;
        font-size: 27px;
        line-height: 1.55;
        max-width: 460px;
        margin: 0 auto;
    }}

    .message strong {{
        color: {TERRACOTA};
        font-weight: 600;
    }}

    .divider {{
        width: 60px;
        height: 1px;
        background: {OLIVA};
        opacity: 0.4;
        margin: 34px auto;
    }}

    .big-day {{
        font-family: 'Cormorant Garamond', serif;
        font-size: 96px;
        line-height: 1;
        color: {TERRACOTA};
    }}

    .month {{
        font-family: 'Montserrat', sans-serif;
        font-size: 15px;
        letter-spacing: 4px;
        margin-top: 6px;
    }}

    .time {{
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 24px;
        margin-top: 22px;
    }}

    .venue {{
        font-family: 'Montserrat', sans-serif;
        font-size: 14px;
        letter-spacing: 1px;
        color: {OLIVA};
        margin-top: 10px;
    }}

    .body-text {{
        font-family: 'Cormorant Garamond', serif;
        font-size: 24px;
        line-height: 1.5;
        max-width: 440px;
        margin: 0 auto;
    }}

    .button {{
        display: inline-block;
        margin-top: 32px;
        padding: 16px 34px;
        background: {TERRACOTA};
        color: {BLANCO} !important;
        font-family: 'Montserrat', sans-serif;
        font-size: 13px;
        letter-spacing: 2px;
        text-decoration: none;
        border-radius: 999px;
    }}

    .monogram {{
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 46px;
        color: {OLIVA};
    }}

    @media (max-width: 480px) {{
        .names {{ font-size: 54px; }}
        section {{ padding: 70px 20px; }}
        .message {{ font-size: 23px; }}
        .big-day {{ font-size: 78px; }}
        .guest-name {{ font-size: 28px; }}
    }}

    </style>
    """
)


# =========================================================
# PORTADA
# =========================================================

fondo_portada = estilo_hero(foto_portada, posicion_portada)

html_block(
    f"""
    <section class="hero" {fondo_portada}>
        <div class="hero-content">
            <div class="eyebrow">NOS CASAMOS</div>
            <div class="names">Valeria <em>&</em> Hector</div>
            <div class="subtitle">Queremos que seas parte de nuestra historia</div>
            <div class="branch">❧</div>
        </div>
    </section>
    """
)


# =========================================================
# MENSAJE / PETICIÓN DE PADRINOS
# =========================================================

html_block(
    f"""
    <section class="section-beige">
        <div class="section-label">Una petición especial</div>
        <div class="guest-name">{nombre_invitado}</div>
        <div class="message">{MENSAJE}</div>
        <div class="divider"></div>
        <div class="body-text">{CUERPO}</div>
    </section>
    """
)


# =========================================================
# FECHA
# =========================================================

html_block(
    f"""
    <section class="section-white">
        <div class="section-label">Fecha</div>
        <div class="big-day">{FECHA_DIA}</div>
        <div class="month">{FECHA_MES}</div>
        <div class="time">{HORA}</div>
        <div class="venue">{LUGAR} · {CIUDAD}</div>
    </section>
    """
)


# =========================================================
# CONFIRMACIÓN
# =========================================================

html_block(
    f"""
    <section class="section-beige">
        <div class="section-label">¿Contamos contigo?</div>
        <div class="body-text">
            Confírmanos si aceptas ser nuestro padrino o madrina,
            para poder darte todos los detalles.
        </div>
        <a class="button" href="{FORMS_URL}" target="_blank">
            ✉ &nbsp; SÍ, QUIERO SER PADRINO/MADRINA
        </a>
    </section>
    """
)


# =========================================================
# CIERRE
# =========================================================

html_block(
    """
    <section class="section-white" style="padding:70px 24px;">
        <div class="monogram">VH</div>
    </section>
    """
)
