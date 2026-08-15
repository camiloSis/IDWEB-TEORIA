# Diagnóstico Formal de Auditoría — IDWEB-TEORIA

**Versión:** 1.0  
**Fecha:** 2026-08-08  
**Tipo:** Auditoría técnica + plan de modificación asistida por agente IA  
**Estado:** Diagnóstico previo a modificación  
**Proyecto:** IDWEB-TEORIA  
**Objetivo:** Adaptar y mejorar el proyecto sin perder su funcionalidad ni su propósito académico.

---

# 1. Resumen ejecutivo

El proyecto IDWEB-TEORIA es una aplicación web individual que integra:

- HTML/CSS/JavaScript en el frontend.
- Un servidor HTTP implementado directamente con la biblioteca estándar de Python.
- MySQL como base de datos.
- Docker Compose para ejecutar web + MySQL + phpMyAdmin.

La arquitectura general es válida para un proyecto académico y permite demostrar integración entre frontend, backend y base de datos.

Sin embargo, la implementación presenta varios problemas de seguridad, configuración, documentación y mantenibilidad.

### Evaluación general

| Área | Estado |
|---|---|
| Arquitectura general | 🟢 Correcta |
| Frontend | 🟢/🟡 |
| Backend | 🟡 |
| Base de datos | 🟢/🟡 |
| Docker | 🟠 |
| Seguridad | 🔴 |
| Documentación | 🟠 |
| Mantenibilidad | 🟡 |
| Preparación para migración | 🟠 |

**Conclusión:** el proyecto es recuperable y no necesita ser reconstruido desde cero. Se recomienda una modificación controlada y por etapas.

---

# 2. Inventario auditado

Se revisaron directamente:

```text
proyectoindividual.html
styles.css
script.js
app.py
init.sql
requirements.txt
dockerfile
docker-compose.yml
ESTRUCTURA.md
img/*
.git/*
.vscode/*
```

También se revisó el historial Git disponible.

La estructura real coincide en gran medida con la estructura documentada.

---

# 3. Arquitectura real detectada

La documentación describe el proyecto como un frontend + backend + MySQL.

La arquitectura real es más específicamente:

```text
Navegador
   │
   ├── proyectoindividual.html
   ├── styles.css
   ├── script.js
   └── img/
   │
   │ HTTP POST
   ▼
Python http.server
   │
   └── app.py
        │
        ▼
mysql-connector-python
        │
        ▼
MySQL 8.0
```

Docker agrega:

```text
docker-compose.yml
│
├── web
│   └── Python
│
├── db
│   └── MySQL 8.0
│
└── phpmyadmin
```

## Corrección importante de documentación

El proyecto **no utiliza Flask**.

Utiliza:

```python
http.server
socketserver
```

Por tanto, cualquier documentación que lo describa como Flask debe corregirse.

---

# 4. Hallazgos críticos

## AUD-SEC-001 — Autenticación administrativa insegura

**Severidad:** 🔴 Crítica  
**Prioridad:** P1  
**Archivo:** `app.py`  
**Zona:** `do_GET()`  
**Líneas:** 33–43

### Evidencia

Actualmente:

```python
if params.get('pass') == ['1234']:
```

El acceso se realiza mediante:

```text
/admin?pass=1234
```

### Problemas

- Contraseña hardcodeada.
- Contraseña extremadamente débil.
- Credencial enviada mediante URL.
- Puede quedar registrada en historial, logs o herramientas del navegador.
- No existe sesión.
- No existe expiración.
- No existe mecanismo de logout.
- No existe control de intentos.

### Instrucción para el agente

Implementar una autenticación mínima pero apropiada para el alcance del proyecto.

Preferencia:

- credencial administrativa mediante variable de entorno;
- formulario `/admin/login`;
- sesión/cookie para mantener autenticación;
- `/admin` debe comprobar la sesión;
- agregar `/admin/logout`;
- no colocar contraseñas en la URL.

### Restricción

No introducir un framework de autenticación complejo si no es necesario.

No modificar la funcionalidad pública del formulario.

---

## AUD-SEC-002 — Stored XSS en panel administrativo

**Severidad:** 🔴 Crítica  
**Prioridad:** P1  
**Archivo:** `app.py`  
**Zona:** `mostrar_admin()`  
**Líneas:** 96–103

### Evidencia

Los datos recuperados de MySQL se concatenan directamente:

```python
html += f"<tr><td>{f[0]}</td><td>{f[1]}</td><td>{f[2]}</td><td>{f[3]}</td><td>{f[4]}</td></tr>"
```

### Riesgo

Un usuario podría almacenar HTML/JavaScript dentro de un mensaje y posteriormente ejecutar código cuando el administrador consulte el panel.

### Instrucción para el agente

Escapar correctamente todos los valores dinámicos antes de insertarlos en HTML.

Si se mantiene la generación HTML desde Python, utilizar una función segura como:

```python
html.escape(...)
```

para:

- nombre;
- email;
- asunto;
- mensaje;
- fecha.

No permitir que el contenido enviado por el usuario sea interpretado como HTML.

### Criterio de aceptación

Un mensaje como:

```html
<script>alert('XSS')</script>
```

debe mostrarse como texto y nunca ejecutarse.

---

## AUD-SEC-003 — Credenciales hardcodeadas

**Severidad:** 🔴 Crítica  
**Prioridad:** P1  
**Archivos:**

```text
app.py
docker-compose.yml
```

### Evidencia

`app.py`:

```python
'password': 'tus_password'
```

`docker-compose.yml`:

```yaml
MYSQL_ROOT_PASSWORD: tus_password
```

### Instrucción para el agente

Eliminar credenciales del código fuente.

Utilizar variables de entorno.

Por ejemplo:

```text
DB_HOST
DB_USER
DB_PASSWORD
DB_NAME
ADMIN_PASSWORD
```

El agente puede crear:

```text
.env.example
```

con valores de ejemplo.

### Importante

No crear ni incluir un `.env` real con secretos en el repositorio.

Agregar `.env` al `.gitignore`.

---

## AUD-SEC-004 — Posible exposición de archivos privados

**Severidad:** 🔴 Crítica  
**Prioridad:** P1  
**Archivo:** `app.py`

### Evidencia

El handler hereda de:

```python
http.server.SimpleHTTPRequestHandler
```

y finalmente ejecuta:

```python
return http.server.SimpleHTTPRequestHandler.do_GET(self)
```

Esto hace que el servidor pueda utilizar el directorio del proyecto como raíz de archivos estáticos.

El proyecto contiene archivos que no deberían considerarse recursos públicos:

```text
app.py
init.sql
docker-compose.yml
requirements.txt
.git/
.vscode/
```

### Instrucción para el agente

Separar los recursos públicos del código privado.

Crear una estructura similar a:

```text
public/
├── proyectoindividual.html
├── styles.css
├── script.js
└── img/
```

El servidor debe servir solamente `public/`.

El backend debe continuar ejecutándose fuera de la raíz pública.

### Restricción

No borrar los archivos originales.

Reubicar y actualizar las rutas necesarias.

---

# 5. Problemas importantes de Docker

## AUD-INF-001 — Nombre de Dockerfile

**Severidad:** 🔴 Crítica  
**Prioridad:** P1  
**Archivo:** `dockerfile`

Actualmente:

```text
dockerfile
```

y Compose utiliza:

```yaml
build: .
```

En Linux, Docker normalmente busca:

```text
Dockerfile
```

### Instrucción para el agente

Renombrar:

```text
dockerfile
```

a:

```text
Dockerfile
```

No duplicarlo.

Actualizar referencias si existen.

---

## AUD-INF-002 — Falta `.dockerignore`

**Severidad:** 🟠 Importante  
**Prioridad:** P2

El Dockerfile utiliza:

```dockerfile
COPY . .
```

y el proyecto contiene:

```text
.git/
.vscode/
```

### Instrucción

Crear `.dockerignore` con exclusiones apropiadas:

```text
.git
.vscode
__pycache__
*.pyc
.env
```

No excluir recursos necesarios para ejecutar la aplicación.

---

## AUD-INF-003 — `depends_on` no espera a MySQL

**Severidad:** 🟠 Importante  
**Prioridad:** P2

Actualmente:

```yaml
depends_on:
  - db
```

Esto no garantiza que MySQL esté listo para aceptar conexiones.

### Instrucción

Agregar `healthcheck` a MySQL y utilizarlo como condición de disponibilidad si la versión de Compose utilizada lo permite.

Alternativamente, implementar reintentos de conexión en Python.

Preferencia:

1. healthcheck;
2. reintentos razonables en el backend si siguen siendo necesarios.

---

## AUD-INF-004 — Mezcla de imagen construida y volumen de código

**Severidad:** 🟠 Importante  
**Prioridad:** P2

Dockerfile:

```dockerfile
COPY . .
```

Compose:

```yaml
volumes:
  - .:/app
```

El volumen termina ocultando el contenido copiado a `/app`.

### Diagnóstico

Esto puede ser válido en desarrollo, pero la configuración no está claramente separada entre desarrollo y producción.

### Instrucción

Para esta fase, priorizar un entorno de **desarrollo reproducible**.

No crear una arquitectura de producción innecesariamente compleja.

Mantener el volumen si facilita el desarrollo, pero documentar claramente su propósito.

---

## AUD-INF-005 — Versión antigua de Python

**Severidad:** 🟡 Mejorable  
**Prioridad:** P3  
**Archivo:** `Dockerfile`

Actualmente:

```dockerfile
FROM python:3.9-slim
```

### Instrucción

No actualizar automáticamente a la última versión.

Primero detectar la versión Python disponible en el entorno actual y verificar compatibilidad con:

```text
mysql-connector-python
```

Después utilizar una versión estable compatible.

---

# 6. Problemas de backend

## AUD-BE-001 — Validación insuficiente en servidor

**Severidad:** 🔴 Crítica  
**Prioridad:** P1

El frontend valida los datos, pero el backend acepta directamente:

```python
nombre
email
asunto
mensaje
```

### Problema

Un cliente puede ignorar completamente JavaScript y enviar un POST manual.

### Instrucción

Implementar validación backend:

- campos requeridos;
- longitud mínima/máxima;
- email válido;
- tamaño máximo del mensaje;
- normalización básica de espacios.

Los límites deben ser coherentes con `init.sql`.

### Importante

La validación frontend debe conservarse.

La validación backend es adicional.

---

## AUD-BE-002 — Sin límite de tamaño de request

**Severidad:** 🟠 Importante  
**Prioridad:** P2

Actualmente:

```python
content_length = int(self.headers['Content-Length'])
post_data = self.rfile.read(content_length)
```

No hay límite máximo.

### Instrucción

Definir un límite razonable para solicitudes del formulario.

Si se supera:

```text
413 Payload Too Large
```

o una respuesta equivalente.

---

## AUD-BE-003 — Exposición de excepciones

**Severidad:** 🟠 Importante  
**Prioridad:** P2

Actualmente:

```python
self.wfile.write(f"Error al consultar DB: {e}".encode('utf-8'))
```

### Problema

El cliente puede recibir detalles internos.

### Instrucción

Registrar el error en servidor y devolver un mensaje genérico.

No mostrar excepciones internas al usuario.

---

## AUD-BE-004 — Conexión MySQL por solicitud

**Severidad:** 🟡 Mejorable  
**Prioridad:** P3

Cada operación crea una nueva conexión.

Para este proyecto pequeño es funcional.

### Instrucción

No implementar un sistema complejo todavía.

Puede mantenerse durante esta fase.

Documentar como mejora futura si se desea.

---

## AUD-BE-005 — Uso de root desde la aplicación

**Severidad:** 🟠 Importante  
**Prioridad:** P2

Actualmente:

```text
user: root
```

### Instrucción

Crear un usuario específico para la aplicación con permisos únicamente sobre:

```text
proyecto_db
```

El root debe reservarse para administración.

---

# 7. Problemas de CORS

## AUD-BE-006 — CORS global innecesario

**Severidad:** 🟠 Importante  
**Prioridad:** P2

Actualmente:

```python
Access-Control-Allow-Origin: *
```

Además, el formulario no utiliza AJAX.

### Instrucción

Después de reorganizar frontend/backend:

- eliminar CORS si no es necesario;
- o restringirlo al origen concreto si realmente se requiere.

No conservar `*` por defecto.

---

# 8. Problemas del frontend

## AUD-FE-001 — URL backend hardcodeada

**Severidad:** 🟠 Importante  
**Prioridad:** P2

Actualmente:

```html
<form action="http://localhost:5002/submit_contact" method="POST">
```

### Problema

Acopla el frontend a:

```text
localhost:5002
```

### Instrucción

Utilizar una ruta relativa:

```text
/submit_contact
```

si frontend y backend son servidos por el mismo servidor.

Esto también elimina la necesidad de CORS para el formulario.

---

## AUD-FE-002 — Documentación incorrecta sobre AJAX

**Severidad:** 🟡 Mejorable  
**Prioridad:** P3

`ESTRUCTURA.md` afirma que el formulario usa AJAX.

No es cierto.

### Instrucción

Actualizar la documentación para indicar:

```text
Formulario HTML → POST /submit_contact → app.py → MySQL
```

---

## AUD-FE-003 — Eventos inline

**Severidad:** 🟡 Mejorable  
**Prioridad:** P3

Ejemplo:

```html
onclick="showTab('sobreMi', event)"
```

### Instrucción

No es necesario cambiarlo durante la corrección mínima.

Si el agente refactoriza JavaScript, puede migrar a:

```javascript
addEventListener()
```

pero debe evitar alterar el comportamiento visual.

---

## AUD-FE-004 — `console.log()` de desarrollo

**Severidad:** 🟡 Mejorable  
**Prioridad:** P3

Existen numerosos `console.log()`.

### Instrucción

Eliminar los mensajes puramente pedagógicos/debug si no son necesarios para el funcionamiento.

No eliminar mensajes útiles sin revisar su propósito.

---

## AUD-FE-005 — Error ortográfico en clase CSS

**Severidad:** 🟡 Mejorable  
**Prioridad:** P3

Existe:

```html
class="columa-foto"
```

Probablemente debería ser:

```text
columna-foto
```

### Instrucción

Comprobar primero si la clase aparece en CSS.

Si existe la correspondencia correcta, normalizar nombre HTML/CSS.

---

# 9. CSS

## AUD-CSS-001 — Uso elevado de `!important`

**Severidad:** 🟡 Mejorable  
**Prioridad:** P3

Se detectaron varios usos de:

```css
!important
```

### Instrucción

No eliminarlos masivamente.

Revisarlos uno por uno y retirar solamente aquellos que puedan eliminarse sin modificar el diseño.

La apariencia visual tiene prioridad sobre una "limpieza" superficial.

---

## AUD-CSS-002 — Responsive correcto

**Severidad:** 🟢 Correcto

Existen media queries para:

```text
768px
600px
```

No modificar esta parte salvo que una prueba revele un problema real.

---

# 10. Base de datos

## AUD-DB-001 — Tabla funcional

**Severidad:** 🟢 Correcto

La tabla:

```sql
mensajes_contacto
```

tiene:

- ID;
- nombre;
- email;
- asunto;
- mensaje;
- fecha.

La estructura es suficiente para el alcance actual.

---

## AUD-DB-002 — Campos sin `NOT NULL`

**Severidad:** 🟡 Mejorable  
**Prioridad:** P3

Actualmente los campos permiten `NULL`.

### Instrucción

Considerar:

```sql
nombre VARCHAR(100) NOT NULL
email VARCHAR(100) NOT NULL
asunto VARCHAR(200) NOT NULL
mensaje TEXT NOT NULL
```

siempre que esto sea compatible con el flujo existente.

---

# 11. Ejecución local

## AUD-ENV-001 — Puerto inconsistente

**Severidad:** 🟠 Importante  
**Prioridad:** P2

Backend:

```python
PORT = 5000
```

Docker:

```text
5002:5000
```

Frontend:

```text
localhost:5002
```

Si se ejecuta directamente:

```bash
python app.py
```

el backend queda en:

```text
localhost:5000
```

pero el frontend intenta usar:

```text
localhost:5002
```

### Instrucción

Cambiar el formulario a:

```text
/submit_contact
```

y utilizar el mismo servidor para frontend/backend.

Esto hace que Docker y ejecución local sean coherentes.

---

# 12. Git

## AUD-GIT-001 — Repositorio incluido en el ZIP

**Severidad:** 🟡 Mejorable

El ZIP contiene:

```text
.git/
```

### Diagnóstico

Esto no es un error del proyecto.

Es útil para preservar el historial.

Sin embargo, `.git` no debería entrar en la imagen Docker.

### Instrucción

Conservar `.git` si el objetivo es mantener el repositorio.

Excluirlo mediante `.dockerignore`.

---

## AUD-GIT-002 — Historial con credenciales de ejemplo

Se verificó que las cadenas de ejemplo aparecen en el historial.

No se detectó evidencia de una contraseña real distinta de las credenciales de prueba revisadas.

### Instrucción

Si esas credenciales fueron siempre ficticias:

- rotarlas igualmente durante la migración;
- no reutilizarlas.

Si alguna vez fueron reales:

- cambiarlas;
- revisar historial;
- considerar limpieza del historial Git.

---

# 13. Documentación

## AUD-DOC-001 — `ESTRUCTURA.md` necesita actualización

**Severidad:** 🟠 Importante

Debe corregir:

```text
"AJAX"
```

por:

```text
"POST HTML tradicional"
```

y cualquier referencia a Flask por:

```text
"servidor HTTP implementado con http.server"
```

También debe actualizar la descripción de ejecución local.

---

# 14. Cambios que el agente NO debe realizar automáticamente

El agente debe abstenerse de:

- migrar a Flask/FastAPI sin autorización;
- cambiar MySQL por PostgreSQL;
- cambiar Docker por otra tecnología;
- rediseñar visualmente el sitio;
- cambiar textos personales;
- eliminar imágenes;
- eliminar `.git`;
- borrar commits;
- modificar la identidad o contenido académico;
- añadir dependencias innecesarias;
- convertir todo el proyecto a una arquitectura empresarial;
- implementar autenticación compleja innecesaria;
- actualizar Python sin comprobar compatibilidad;
- modificar el esquema de BD sin comprobar el código que lo utiliza.

---

# 15. Orden recomendado de ejecución del agente

El agente debe trabajar en este orden.

## Fase 1 — Seguridad

Resolver:

```text
AUD-SEC-001
AUD-SEC-002
AUD-SEC-003
AUD-SEC-004
AUD-BE-001
AUD-BE-003
```

## Fase 2 — Infraestructura

Resolver:

```text
AUD-INF-001
AUD-INF-002
AUD-INF-003
AUD-INF-004
AUD-ENV-001
```

## Fase 3 — Backend

Resolver:

```text
AUD-BE-002
AUD-BE-005
AUD-BE-006
```

## Fase 4 — Frontend

Resolver:

```text
AUD-FE-001
AUD-FE-002
AUD-FE-005
```

## Fase 5 — Calidad

Opcional:

```text
AUD-FE-003
AUD-FE-004
AUD-CSS-001
AUD-DB-002
```

---

# 16. Criterios de aceptación

El agente debe considerar la modificación exitosa únicamente si:

### Aplicación

- [ ] La página principal sigue funcionando.
- [ ] Las pestañas siguen funcionando.
- [ ] El diseño visual no cambia innecesariamente.
- [ ] Las imágenes continúan cargando.
- [ ] El formulario continúa funcionando.

### Backend

- [ ] `POST /submit_contact` funciona.
- [ ] Los datos llegan a MySQL.
- [ ] El backend valida datos independientemente del frontend.
- [ ] No se muestran excepciones internas.
- [ ] No existe contraseña administrativa en la URL.

### Seguridad

- [ ] No existen contraseñas hardcodeadas.
- [ ] El panel administrativo requiere autenticación.
- [ ] Los datos mostrados en `/admin` están escapados.
- [ ] No se puede ejecutar JavaScript enviado mediante el formulario.
- [ ] No se sirven archivos privados como recursos públicos.

### Docker

- [ ] `docker compose build` funciona.
- [ ] `docker compose up` funciona.
- [ ] MySQL queda operativo.
- [ ] Python puede conectarse a MySQL.
- [ ] phpMyAdmin puede conectarse a MySQL.
- [ ] El sitio funciona en el puerto documentado.

### Documentación

- [ ] `ESTRUCTURA.md` refleja la arquitectura real.
- [ ] Se documenta que el backend utiliza `http.server`.
- [ ] Se elimina la afirmación incorrecta de AJAX.
- [ ] Se documentan las nuevas variables de entorno.
- [ ] Se documenta la forma correcta de iniciar el proyecto.

---

# 17. Instrucciones directas para el agente de IA

El siguiente bloque puede utilizarse como instrucción de trabajo para un agente:

```text
AUDITA Y MODIFICA EL PROYECTO IDWEB-TEORIA SEGÚN EL DOCUMENTO
"Diagnóstico Formal de Auditoría — IDWEB-TEORIA".

OBJETIVO

Adaptar y mejorar el proyecto existente sin reconstruirlo desde cero,
sin alterar innecesariamente su diseño y sin introducir tecnologías
que no sean necesarias.

REGLA PRINCIPAL

Primero inspecciona el estado actual del repositorio y luego realiza
las modificaciones. No inventes archivos, dependencias ni arquitectura.

DEBES PRESERVAR

- diseño visual actual;
- contenido personal;
- imágenes;
- funcionalidad de pestañas;
- formulario de contacto;
- almacenamiento de mensajes;
- MySQL;
- Docker Compose;
- propósito académico del proyecto.

CAMBIOS OBLIGATORIOS

1. Corregir autenticación administrativa:
   - eliminar ?pass=1234;
   - utilizar credencial mediante variable de entorno;
   - implementar sesión/cookie;
   - proteger /admin;
   - agregar logout si es necesario.

2. Corregir XSS en /admin:
   - escapar todos los datos provenientes de MySQL
     antes de insertarlos en HTML.

3. Eliminar credenciales hardcodeadas:
   - app.py;
   - docker-compose.yml.
   - crear .env.example;
   - ignorar .env mediante .gitignore.

4. Evitar que el servidor exponga archivos privados:
   - crear public/;
   - colocar allí HTML, CSS, JS e imágenes;
   - servir únicamente public/ como contenido público;
   - mantener app.py, SQL y configuración fuera de la raíz pública.

5. Renombrar dockerfile a Dockerfile.

6. Crear .dockerignore.

7. Corregir disponibilidad de MySQL mediante healthcheck
   o una estrategia equivalente.

8. Corregir el formulario:
   - usar /submit_contact en lugar de localhost:5002;
   - mantener POST tradicional si no existe una razón para migrarlo a AJAX.

9. Implementar validación backend:
   - campos obligatorios;
   - límites de longitud;
   - email válido;
   - límite de tamaño de request.

10. No mostrar excepciones internas al cliente.

11. Utilizar un usuario MySQL específico para la aplicación
    en lugar de root cuando sea viable sin romper el entorno.

12. Eliminar CORS global si deja de ser necesario.

13. Corregir ESTRUCTURA.md:
    - no mencionar Flask;
    - no mencionar AJAX;
    - documentar http.server;
    - actualizar ejecución local;
    - documentar variables de entorno.

CAMBIOS OPCIONALES

Solo si no afectan el funcionamiento:

- eliminar console.log de debug;
- corregir "columa-foto";
- reducir !important;
- mejorar NOT NULL en SQL;
- separar eventos inline.

NO HACER

- no migrar a Flask/FastAPI;
- no cambiar MySQL;
- no cambiar Docker;
- no rediseñar la web;
- no eliminar .git;
- no borrar historial;
- no cambiar contenido personal;
- no introducir dependencias innecesarias;
- no actualizar Python arbitrariamente.

VALIDACIÓN FINAL

Antes de terminar:

1. Ejecutar comprobación sintáctica de Python.
2. Construir Docker.
3. Levantar Docker Compose.
4. Comprobar conexión Python → MySQL.
5. Comprobar página principal.
6. Comprobar pestañas.
7. Enviar un mensaje de contacto.
8. Confirmar que aparece en MySQL.
9. Comprobar /admin sin autenticación.
10. Comprobar login administrativo.
11. Comprobar logout.
12. Probar mensaje con HTML/JavaScript y confirmar que NO se ejecuta.
13. Comprobar que archivos privados no son servidos.
14. Comprobar phpMyAdmin.
15. Revisar git diff.

AL FINAL

Genera un informe indicando:

- archivos modificados;
- archivos creados;
- archivos renombrados;
- cambios realizados;
- pruebas ejecutadas;
- pruebas exitosas;
- problemas restantes;
- cambios que deliberadamente NO realizaste;
- cualquier decisión que requiera aprobación humana.

No declares que el proyecto funciona correctamente si no ejecutaste
las pruebas correspondientes.
```

---

# 18. Qué puede modificar directamente el agente

## 🟢 Puede hacerlo directamente

- `app.py`
- `docker-compose.yml`
- `Dockerfile`
- `.dockerignore`
- `.gitignore`
- `.env.example`
- `init.sql`
- `proyectoindividual.html`
- `script.js`
- `ESTRUCTURA.md`
- reorganización de archivos públicos.

## 🟡 Puede hacerlo, pero debe verificar

- actualización de Python;
- cambios de esquema MySQL;
- creación de usuario MySQL;
- cambios de dependencias;
- modificaciones de CSS;
- refactorización de JavaScript.

## 🔴 No debería hacerlo sin autorización

- cambiar de framework;
- cambiar de base de datos;
- cambiar la arquitectura completa;
- eliminar historial Git;
- cambiar contenido personal;
- rediseñar la página;
- publicar/desplegar;
- eliminar información original.

---

# 19. Resultado esperado después de la intervención

La arquitectura objetivo debería quedar aproximadamente así:

```text
IDWEB-TEORIA/
│
├── public/
│   ├── proyectoindividual.html
│   ├── styles.css
│   ├── script.js
│   └── img/
│       ├── carnet.jpg
│       ├── sistemas.png
│       └── unsa.png
│
├── app.py
├── init.sql
├── requirements.txt
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env.example
│
├── .git/
├── .vscode/
└── ESTRUCTURA.md
```

Y el flujo:

```text
                    ┌───────────────┐
                    │   Navegador   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    app.py     │
                    │ http.server   │
                    └───────┬───────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
        Archivos públicos             /submit_contact
              │                           │
              │                           ▼
              │                    ┌──────────────┐
              │                    │    MySQL     │
              │                    └──────────────┘
              │
              └──────────────► /admin
                                  │
                                  ▼
                           autenticación
                                  │
                                  ▼
                         mensajes escapados
```

---

# 20. Veredicto final de la auditoría

**No recomiendo descartar el proyecto.**

La base es perfectamente aprovechable.

La prioridad es corregir primero:

```text
🔴 Autenticación
🔴 XSS
🔴 Credenciales
🔴 Exposición de archivos
🔴 Dockerfile
🔴 Validación backend
```

Después:

```text
🟠 Docker
🟠 CORS
🟠 configuración
🟠 documentación
🟠 usuario MySQL
```

Y finalmente:

```text
🟡 limpieza
🟡 refactorización
🟡 calidad del código
```

La idea no es convertir un proyecto académico sencillo en una aplicación empresarial. La meta es **llevarlo de "funciona en mi antiguo entorno" a "es reproducible, razonablemente seguro, documentado y mantenible en tu entorno actual"**.

---

# 21. Regla de oro para la siguiente fase

Antes de ejecutar al agente, conserva una copia intacta del ZIP original:

```text
IDWEB-TEORIA_original.zip
```

El agente debe trabajar sobre una copia:

```text
IDWEB-TEORIA/
```

y sus modificaciones deben poder revisarse mediante:

```bash
git diff
```

La auditoría queda entonces como la **línea base oficial** contra la cual podemos comprobar si la intervención del agente realmente solucionó los problemas detectados.
