# Estructura del Proyecto IDWEB-TEORIA

Página web personal (proyecto individual) que integra frontend, backend y base de datos
PostgreSQL.

## Árbol de archivos

```
IDWEB-TEORIA/
├── public/                      # Recursos públicos (única raíz servida al navegador)
│   ├── proyectoindividual.html  #   Página principal con pestañas (362 líneas)
│   ├── styles.css               #   Estilos visuales de la página (279 líneas)
│   ├── script.js                #   Lógica del cliente: pestañas, validación de formulario
│   └── img/                     #   Imágenes de la página
│       ├── carnet.jpg           #     Foto de perfil
│       ├── sistemas.png         #     Logo Ingeniería de Sistemas
│       └── unsa.png             #     Logo UNSA
├── app.py                       # Backend: servidor HTTP + API + panel admin
├── init.sql                     # Referencia de la estructura PostgreSQL (no recrea la BD)
├── requirements.txt             # Dependencias Python (psycopg2-binary)
├── Dockerfile                   # Imagen Python para el contenedor web
├── docker-compose.yml           # Orquestación: solo la app web (PostgreSQL es externo)
├── .dockerignore                # Exclusiones del contexto de build
├── .gitignore                   # Exclusiones de Git (.env, __pycache__, etc.)
├── .env.example                 # Plantilla de variables de entorno (copiar a .env)
├── .git/                        # Repositorio Git
├── .vscode/                     # Configuración de VS Code
├── ESTRUCTURA.md                # Este documento
├── INFORME_INTERVENCION.md      # Informe de la auditoría anterior
└── Diagnostico_Formal_Auditoria_IDWEB-TEORIA.md   # Auditoría técnica
```

## Arquitectura

Backend sin framework: servidor HTTP implementado con la biblioteca estándar de
Python (`http.server` + `socketserver`). No se usa Flask ni AJAX.

**La base de datos es PostgreSQL, externa al proyecto y administrada por el
usuario mediante pgAdmin 4.** El proyecto no levanta contenedores MySQL ni
phpMyAdmin.

```
Navegador
   │
   ├── public/proyectoindividual.html + styles.css + script.js
   │
   │  POST tradicional (formulario HTML)
   ▼
app.py (http.server)
   │
   ├── /submit_contact ──► PostgreSQL (externo: proyecto_db.public.mensajes_contacto)
   ├── /admin            ──► requiere sesión (login + cookie)
   └── /admin/login      ──► verifica ADMIN_USER / ADMIN_PASSWORD
                                          ▲
                                   pgAdmin 4 (usuario)
```

## Base de datos (PostgreSQL externo)

| Elemento | Valor |
|----------|-------|
| Base de datos | `proyecto_db` |
| Schema | `public` |
| Tabla | `mensajes_contacto` |
| Puerto PostgreSQL | `5432` |
| Columna fecha | `fecha` |

La BD y la tabla ya existen y funcionan. `init.sql` es solo referencia de
estructura para reconstruirla en un entorno nuevo; **no se ejecuta
automáticamente ni contiene instrucciones destructivas**.

Consulta de verificación desde pgAdmin 4:

```sql
SELECT *
FROM mensajes_contacto
ORDER BY fecha DESC;
```

## Capas del proyecto

| Capa        | Archivo(s)              | Descripción |
|-------------|-------------------------|-------------|
| Frontend    | `public/proyectoindividual.html`, `public/styles.css`, `public/script.js` | Página de presentación con pestañas y formulario de contacto (POST tradicional, sin AJAX) |
| Backend     | `app.py`                | Servidor HTTP con `http.server`, valida datos, guarda en PostgreSQL, panel admin con sesión |
| Base de datos | externa (PostgreSQL) | `proyecto_db.public.mensajes_contacto`, administrada con pgAdmin 4 |
| Infraestructura | `Dockerfile`, `docker-compose.yml` | Contenedor web (puerto 5002) |

## Variables de entorno

No hay credenciales hardcodeadas. Copiar `.env.example` a `.env`:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `POSTGRES_HOST` | Host de PostgreSQL | `localhost` (local y Docker con `network_mode: host`) |
| `POSTGRES_PORT` | Puerto de PostgreSQL | `5432` |
| `POSTGRES_DB` | Nombre de la BD | `proyecto_db` |
| `POSTGRES_USER` | Usuario PostgreSQL | `postgres` |
| `POSTGRES_PASSWORD` | Contraseña PostgreSQL | `CHANGE_ME` |
| `ADMIN_USER` | Usuario del panel admin | `admin` |
| `ADMIN_PASSWORD` | Contraseña del panel admin | `admin123` |
| `PORT` | Puerto del servidor Python | `5000` |

## Diferencia de host local vs Docker

Dentro de un contenedor, `localhost` apunta al propio contenedor, no al host.
Para que el contenedor web acceda al PostgreSQL del sistema **sin exponerlo a la
red**, `docker-compose.yml` usa `network_mode: host` (Linux): el contenedor
comparte la red del host y `localhost:5432` es directamente el PostgreSQL del
sistema (no requiere `host.docker.internal` ni cambiar `listen_addresses`).
La web queda en `http://localhost:5002` (definida con `PORT`).

Nota: `network_mode: host` es específico de Linux; en Docker Desktop
(Windows/macOS) se usaría la IP del host en `POSTGRES_HOST`.

## Puertos y servicios

- Web (Docker): `http://localhost:5002`
- Web (local): `http://localhost:5000`
- PostgreSQL: `localhost:5432` (externo, administrado con pgAdmin 4)
- Panel admin: `/admin` (login en `/admin/login`, logout en `/admin/logout`)

## Flujo de datos

```
Usuario → public/proyectoindividual.html → POST /submit_contact (formulario HTML)
        → app.py (validación backend) → PostgreSQL (proyecto_db.public.mensajes_contacto)
        → /admin (login con sesión) → app.py → tabla en HTML con datos escapados
```

## Formas de ejecutar

1. **Docker Compose** (recomienda la web, PostgreSQL ya está en tu máquina):
   ```bash
   cp .env.example .env   # opcional: ajustar credenciales
   docker compose up --build
   ```

2. **Local** (requiere PostgreSQL accesible):
   ```bash
   pip install -r requirements.txt
   POSTGRES_HOST=localhost POSTGRES_USER=postgres POSTGRES_PASSWORD=tu_clave \
   ADMIN_PASSWORD=tu_admin python app.py
   ```

3. **Estático**: abrir `public/proyectoindividual.html` en el navegador
   (solo la parte visual; formulario y panel admin necesitan backend + PostgreSQL).

## Nota sobre el volumen de desarrollo (AUD-INF-004)

`docker-compose.yml` monta `.:/app` como volumen: está intencionado para
desarrollo, para reflejar los cambios en vivo sin reconstruir la imagen.