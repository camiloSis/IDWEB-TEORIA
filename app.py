import http.server
import socketserver
import urllib.parse
import mysql.connector

# CONFIGURACIÓN DE LA BASE DE DATOS (Individual)
DB_CONFIG = {
    'host': 'db', 
    'user': 'root',
    'password': 'tus_password',
    'database': 'proyecto_db'
}

class MyHandler(http.server.SimpleHTTPRequestHandler):
    
    # Manejo de CORS (Vital para que script.js pueda hablar con Python)
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        # Servir el HTML principal
        if self.path == '/' or self.path.startswith('/?envio='):
            self.path = 'proyectoindividual.html'
        
        # Ruta de administración
        elif self.path.startswith('/admin'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if params.get('pass') == ['1234']:
                self.mostrar_admin()
                return
            else:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Acceso denegado. Introduce ?pass=1234 en la URL")
                return
                
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/submit_contact':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            datos = urllib.parse.parse_qs(post_data.decode('utf-8'))

            nombre = datos.get('nombre', [''])[0]
            email = datos.get('email', [''])[0]
            asunto = datos.get('asunto', [''])[0]
            mensaje = datos.get('mensaje', [''])[0]

            exito = self.guardar_en_db(nombre, email, asunto, mensaje)

            if exito:
                # Redirección con parámetro de éxito para que el JS lo detecte
                self.send_response(303)
                self.send_header('Location', '/?envio=exito')
                self.end_headers()
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Error al guardar en la base de datos")

    def guardar_en_db(self, nombre, email, asunto, mensaje):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            sql = "INSERT INTO mensajes_contacto (nombre, email, asunto, mensaje) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (nombre, email, asunto, mensaje))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error MySQL: {e}")
            return False

    def mostrar_admin(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, email, asunto, mensaje, fecha_envio FROM mensajes_contacto ORDER BY fecha_envio DESC")
            filas = cursor.fetchall()
            
            html = "<html><head><title>Admin Panel</title><style>body{font-family:sans-serif; padding:20px} table{border-collapse:collapse;width:100%} th,td{border:1px solid #ddd;padding:12px;text-align:left} th{background-color:#667eea;color:white}</style></head><body>"
            html += "<h1>Mensajes de Contacto Recibidos</h1><table><tr><th>Nombre</th><th>Email</th><th>Asunto</th><th>Mensaje</th><th>Fecha</th></tr>"
            
            for f in filas:
                html += f"<tr><td>{f[0]}</td><td>{f[1]}</td><td>{f[2]}</td><td>{f[3]}</td><td>{f[4]}</td></tr>"
            
            html += "</table><br><a href='/'>Ir a la Web</a></body></html>"
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            self.wfile.write(f"Error al consultar DB: {e}".encode('utf-8'))

# Puerto interno del contenedor (Docker lo mapea al 5002)
PORT = 5000
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Servidor Individual activo en puerto {PORT} (Interno)")
    httpd.serve_forever()