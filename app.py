import http.server
import socketserver
import urllib.parse
import html as html_lib
import os
import re
import secrets
import sys
import time
import hmac

import psycopg2
from dotenv import load_dotenv

# ============================================
# CONFIGURACIÓN MEDIANTE VARIABLES DE ENTORNO
# ============================================

# Carga el archivo .env del mismo directorio (si existe) sin sobrescribir
# variables ya definidas en el entorno del sistema.
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

PG_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'port': int(os.environ.get('POSTGRES_PORT', '5432')),
    'database': os.environ.get('POSTGRES_DB', 'proyecto_db'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', ''),
}

ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')

# Directorio público (única raíz servida al navegador)
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')

# Límites del formulario de contacto
MAX_REQUEST_SIZE = 16 * 1024  # 16 KB
MAX_LOGIN_SIZE = 4 * 1024     # 4 KB

LIMITES_CAMPOS = {
    'nombre': (2, 100),
    'email': (3, 100),
    'asunto': (0, 200),
    'mensaje': (10, 2000),
}

EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

# Sesiones administrativas en memoria: token -> timestamp de expiración
SESIONES = {}
SESSION_TTL = 2 * 60 * 60  # 2 horas


def log_error(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)


# ============================================
# BASE DE DATOS (PostgreSQL, instancia externa)
# ============================================

def conectar_db(intentos=5, espera=2):
    """Conecta a PostgreSQL con reintentos (útil mientras la BD está disponible)."""
    ultimo_error = None
    for _ in range(intentos):
        try:
            return psycopg2.connect(**PG_CONFIG)
        except Exception as e:
            ultimo_error = e
            time.sleep(espera)
    raise ultimo_error


def guardar_en_db(nombre, email, asunto, mensaje):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        sql = "INSERT INTO mensajes_contacto (nombre, email, asunto, mensaje) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (nombre, email, asunto, mensaje))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        log_error(f"PostgreSQL: {e}")
        return False


def obtener_mensajes():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, email, asunto, mensaje, fecha FROM mensajes_contacto ORDER BY fecha DESC")
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return filas


# ============================================
# AUTENTICACIÓN ADMINISTRATIVA (sesión con cookie)
# ============================================

def crear_sesion():
    token = secrets.token_hex(32)
    SESIONES[token] = time.time() + SESSION_TTL
    return token


def sesion_valida(token):
    if not token:
        return False
    expira = SESIONES.get(token)
    if expira is None:
        return False
    if time.time() > expira:
        SESIONES.pop(token, None)
        return False
    return True


def cerrar_sesion(token):
    SESIONES.pop(token, None)


def credenciales_correctas(usuario, password):
    usuario_ok = hmac.compare_digest(usuario, ADMIN_USER)
    password_ok = hmac.compare_digest(password, ADMIN_PASSWORD)
    return usuario_ok and password_ok


# ============================================
# VALIDACIÓN DEL FORMULARIO
# ============================================

def normalizar_y_validar(datos):
    """Devuelve (campos_validados, lista_de_errores)."""
    errores = []

    def limpiar(clave):
        return (datos.get(clave, [''])[0] or '').strip()

    nombre = limpiar('nombre')
    email = limpiar('email')
    asunto = limpiar('asunto')
    mensaje = limpiar('mensaje')

    if not (LIMITES_CAMPOS['nombre'][0] <= len(nombre) <= LIMITES_CAMPOS['nombre'][1]):
        errores.append('nombre inválido')
    if not (LIMITES_CAMPOS['email'][0] <= len(email) <= LIMITES_CAMPOS['email'][1]) or not EMAIL_REGEX.match(email):
        errores.append('email inválido')
    if len(asunto) > LIMITES_CAMPOS['asunto'][1]:
        errores.append('asunto demasiado largo')
    if not (LIMITES_CAMPOS['mensaje'][0] <= len(mensaje) <= LIMITES_CAMPOS['mensaje'][1]):
        errores.append('mensaje inválido')

    return {'nombre': nombre, 'email': email, 'asunto': asunto, 'mensaje': mensaje}, errores


# ============================================
# VISTAS HTML DEL ADMIN
# ============================================

def pagina_login(mensaje=''):
    cuerpo = ""
    if mensaje:
        cuerpo += f"<p style='color:red'>{html_lib.escape(mensaje)}</p>"
    return f"""<html><head><title>Login Administrativo</title>
<style>body{{font-family:sans-serif;padding:20px;display:flex;justify-content:center;align-items:center;height:100vh}}
.tarjeta{{border:1px solid #ddd;border-radius:12px;padding:30px;width:320px;box-shadow:0 4px 12px rgba(0,0,0,.1)}}
input{{width:100%;padding:10px;margin:8px 0 16px;border:1px solid #ddd;border-radius:8px;box-sizing:border-box}}
button{{width:100%;padding:12px;background:#667eea;color:white;border:none;border-radius:50px;cursor:pointer}}
h1{{font-size:20px;text-align:center}}</style></head>
<body><div class="tarjeta"><h1>Acceso Administrativo</h1>{cuerpo}
<form action="/admin/login" method="POST">
<label>Usuario:</label><input type="text" name="usuario" required autocomplete="username">
<label>Contraseña:</label><input type="password" name="password" required autocomplete="current-password">
<button type="submit">Ingresar</button>
</form><p style="text-align:center"><a href="/">Volver al sitio</a></p></div></body></html>"""


def pagina_admin(filas):
    html = "<html><head><title>Admin Panel</title><style>body{font-family:sans-serif; padding:20px} table{border-collapse:collapse;width:100%} th,td{border:1px solid #ddd;padding:12px;text-align:left} th{background-color:#667eea;color:white}</style></head><body>"
    html += "<h1>Mensajes de Contacto Recibidos</h1>"
    html += "<p><a href='/admin/logout'>Cerrar sesión</a> | <a href='/'>Ir a la Web</a></p>"
    html += "<table><tr><th>Nombre</th><th>Email</th><th>Asunto</th><th>Mensaje</th><th>Fecha</th></tr>"
    for f in filas:
        celdas = "".join(f"<td>{html_lib.escape(str(v))}</td>" for v in f)
        html += f"<tr>{celdas}</tr>"
    html += "</table></body></html>"
    return html


# ============================================
# SERVIDOR HTTP
# ============================================

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def leer_cuerpo(self, limite):
        content_length = self.headers.get('Content-Length')
        try:
            content_length = int(content_length)
        except (TypeError, ValueError):
            return None
        if content_length > limite:
            return None
        return self.rfile.read(content_length)

    def redirigir(self, destino):
        self.send_response(303)
        self.send_header('Location', destino)
        self.end_headers()

    def responder_error(self, codigo, texto):
        self.send_response(codigo)
        self.end_headers()
        self.wfile.write(texto.encode('utf-8'))

    def do_GET(self):
        ruta = urllib.parse.urlparse(self.path).path

        if ruta == '/' or ruta == '/index.html':
            self.path = '/proyectoindividual.html'

        elif ruta == '/admin':
            cookie = self.headers.get('Cookie', '')
            token = self.extraer_token(cookie)
            if not sesion_valida(token):
                self.redirigir('/admin/login')
                return
            try:
                filas = obtener_mensajes()
                html = pagina_admin(filas)
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            except Exception as e:
                log_error(f"Consulta admin: {e}")
                self.responder_error(500, "Error interno al consultar la base de datos.")
            return

        elif ruta == '/admin/login':
            cookie = self.headers.get('Cookie', '')
            if sesion_valida(self.extraer_token(cookie)):
                self.redirigir('/admin')
                return
            html = pagina_login()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            return

        elif ruta == '/admin/logout':
            cookie = self.headers.get('Cookie', '')
            cerrar_sesion(self.extraer_token(cookie))
            self.send_response(303)
            self.send_header('Location', '/admin/login')
            self.send_header('Set-Cookie', 'admin_session=; Max-Age=0; Path=/')
            self.end_headers()
            return

        return super().do_GET()

    def do_POST(self):
        ruta = urllib.parse.urlparse(self.path).path

        if ruta == '/submit_contact':
            cuerpo = self.leer_cuerpo(MAX_REQUEST_SIZE)
            if cuerpo is None:
                self.responder_error(413, "Solicitud demasiado grande.")
                return
            datos = urllib.parse.parse_qs(cuerpo.decode('utf-8'))
            campos, errores = normalizar_y_validar(datos)
            if errores:
                self.responder_error(400, "Datos inválidos: " + ", ".join(errores))
                return
            if guardar_en_db(**campos):
                self.redirigir('/?envio=exito')
            else:
                self.responder_error(500, "Error interno al guardar el mensaje.")
            return

        if ruta == '/admin/login':
            cookie = self.headers.get('Cookie', '')
            if sesion_valida(self.extraer_token(cookie)):
                self.redirigir('/admin')
                return
            cuerpo = self.leer_cuerpo(MAX_LOGIN_SIZE)
            if cuerpo is None:
                self.responder_error(413, "Solicitud demasiado grande.")
                return
            datos = urllib.parse.parse_qs(cuerpo.decode('utf-8'))
            usuario = (datos.get('usuario', [''])[0] or '')
            password = (datos.get('password', [''])[0] or '')
            if ADMIN_PASSWORD and credenciales_correctas(usuario, password):
                token = crear_sesion()
                self.send_response(303)
                self.send_header('Location', '/admin')
                self.send_header('Set-Cookie', f'admin_session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age={SESSION_TTL}')
                self.end_headers()
            else:
                self.responder_error(401, "Credenciales incorrectas.")
            return

        self.responder_error(404, "Ruta no encontrada.")

    @staticmethod
    def extraer_token(cookie):
        for parte in cookie.split(';'):
            clave, _, valor = parte.strip().partition('=')
            if clave == 'admin_session':
                return valor
        return None

    def log_message(self, format, *args):
        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.address_string(), self.log_date_time_string(), format % args))


PORT = int(os.environ.get('PORT', '5000'))
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Servidor Individual activo en puerto {PORT}")
    httpd.serve_forever()