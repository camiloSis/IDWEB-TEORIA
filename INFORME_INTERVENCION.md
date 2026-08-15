# Informe de Intervención — IDWEB-TEORIA

**Fecha:** 2026-08-08
**Línea base:** `Diagnostico_Formal_Auditoria_IDWEB-TEORIA.md` v1.0
**Backup original:** `/tmp/opencode/IDWEB-TEORIA_original` (copia intacta pre-modificación)

---

## 1. Archivos modificados

| Archivo | Cambios |
|---|---|
| `app.py` | Reescrito: auth por sesión, escape XSS, env vars, validación backend, límite de request, sin CORS, sin excepciones internas, reintentos de conexión |
| `docker-compose.yml` | Env vars, healthcheck MySQL + `depends_on: condition`, usuario de app, quitar credenciales hardcodeadas |
| `init.sql` | Campos `NOT NULL` (AUD-DB-002) |
| `public/proyectoindividual.html` | `action="/submit_contact"` (AUD-FE-001/AUD-ENV-001), `columna-foto` (AUD-FE-005) |
| `public/script.js` | Eliminados 17 `console.log` de debug (AUD-FE-004) |
| `ESTRUCTURA.md` | Reescrito: sin Flask, sin AJAX, documenta `http.server`, env vars, ejecución local (AUD-DOC-001) |

## 2. Archivos creados

- `.env.example` (AUD-SEC-003)
- `.gitignore` (AUD-SEC-003)
- `.dockerignore` (AUD-INF-002)
- `public/` (contenido web, AUD-SEC-004)

## 3. Archivos renombrados

- `dockerfile` → `Dockerfile` (AUD-INF-001)
- `img/` → `public/img/` (parte de AUD-SEC-004)

## 4. Cambios realizados por hallazgo

| Hallazgo | Estado | Detalle |
|---|---|---|
| AUD-SEC-001 | ✅ Resuelto | Login `/admin/login`, cookie de sesión (HttpOnly, SameSite, expira a las 2h), `/admin/logout`, credenciales por env vars, sin contraseña en URL |
| AUD-SEC-002 | ✅ Resuelto | `html.escape()` en los 5 campos del panel admin |
| AUD-SEC-003 | ✅ Resuelto | `DB_*`, `ADMIN_*`, `MYSQL_ROOT_PASSWORD` por entorno; `.env` en `.gitignore` |
| AUD-SEC-004 | ✅ Resuelto | Solo se sirve `public/`; `app.py`, `init.sql`, compose y config devuelven 404 |
| AUD-BE-001 | ✅ Resuelto | Validación backend: requeridos, longitudes, email regex, normalización de espacios |
| AUD-BE-002 | ✅ Resuelto | Límite 16 KB → HTTP 413 |
| AUD-BE-003 | ✅ Resuelto | Errores a stderr; mensajes genéricos al cliente |
| AUD-BE-005 | ✅ Resuelto | Usuario `app_user` (creado por la imagen MySQL vía `MYSQL_USER`), root solo admin |
| AUD-BE-006 | ✅ Resuelto | CORS eliminado (formulario same-origin) |
| AUD-INF-001 | ✅ Resuelto | Renombrado a `Dockerfile` |
| AUD-INF-002 | ✅ Resuelto | `.dockerignore` creado |
| AUD-INF-003 | ✅ Resuelto | Healthcheck MySQL + `service_healthy` + reintentos en Python |
| AUD-INF-004 | ✅ Resuelto | Volumen documentado como intencional para desarrollo |
| AUD-ENV-001 | ✅ Resuelto | `POST /submit_contact` relativo; coherente Docker/local |
| AUD-FE-001 | ✅ Resuelto | Formulario usa ruta relativa |
| AUD-FE-002 | ✅ Resuelto | ESTRUCTURA.md corregido |
| AUD-FE-004 | ✅ Resuelto | `console.log` de debug eliminados |
| AUD-FE-005 | ✅ Resuelto | `columa-foto` → `columna-foto` |
| AUD-DB-002 | ✅ Resuelto | `NOT NULL` en los 4 campos |
| AUD-CSS-001 | ⏸️ No modificado | Los 8 `!important` sostienen la barra sticky; no retiré ninguno (la apariencia tiene prioridad) |
| AUD-FE-003 | ⏸️ No modificado | Eventos inline conservados (el doc lo permite en corrección mínima) |
| AUD-INF-005 | ⏸️ No modificado | Python 3.9-slim conservado; `mysql-connector-python` es compatible (misma versión base verificada con build exitoso) |
| AUD-BE-004 | ⏸️ No modificado | Conexión por request conservada (el doc la permite en esta fase) |
| AUD-GIT-001/002 | ⏸️ No modificado | Historial Git intacto; credenciales de ejemplo quedaron rotadas (las viejas quedan en commits históricos, documentado en la auditoría) |

## 5. Pruebas ejecutadas y resultados

| # | Prueba | Resultado |
|---|---|---|
| 1 | Sintaxis Python (`py_compile`) | ✅ |
| 2 | `docker compose build` | ✅ |
| 3 | `docker compose up` | ✅ (MySQL healthy) |
| 4 | Conexión Python → MySQL | ✅ (mensaje insertado) |
| 5 | Página principal `GET /` | ✅ 200 |
| 6 | Estáticos (css/js/img) | ✅ 200 |
| 7 | Pestañas (handlers `showTab` presentes, JS válido) | ✅ (5 referencias, `node --check` OK) |
| 8 | Envío de mensaje de contacto | ✅ 303 → `/?envio=exito` |
| 9 | Mensaje visible en MySQL | ✅ |
| 10 | `/admin` sin autenticación | ✅ 303 → `/admin/login` |
| 11 | Login incorrecto | ✅ 401 |
| 12 | Login correcto | ✅ 303 → `/admin` + cookie |
| 13 | Logout | ✅ 303 → `/admin/login`; sesión invalidada |
| 14 | XSS `<script>` en mensaje | ✅ Escapado, 0 scripts crudos en el panel |
| 15 | Archivos privados no servidos | ✅ 404 en `app.py`, `init.sql`, `docker-compose.yml`, `requirements.txt`, `.env` |
| 16 | phpMyAdmin | ✅ 200 |
| 17 | Validación backend (mensaje corto / email inválido) | ✅ 400 |
| 18 | Límite de request | ✅ 413 |
| 19 | `/?envio=exito` | ✅ 200 |

## 6. Problemas restantes / pendientes

- La clave `version: '3.8'` en `docker-compose.yml` está obsoleta en Compose v5 (solo warning, no bloquea).
- Las pruebas de pestañas y animaciones en navegador real no se ejecutaron (entorno sin GUI); el JS pasó chequeo sintáctico y las referencias HTML están intactas.
- Los contenedores se detuvieron con `docker compose down -v` al final (se pueden volver a levantar con `docker compose up --build`).

## 7. Cambios deliberadamente NO realizados

- Migrar a Flask/FastAPI, cambiar MySQL o Docker, rediseñar la web, tocar contenido personal, eliminar `.git`, borrar historial, añadir dependencias, cambiar el esquema de BD más allá de `NOT NULL`.

## 8. Decisiones que requieren aprobación humana

1. **Credenciales de ejemplo en `.env.example`** (`admin123`, `app_password`): si se despliega fuera de local, deben cambiarse. La auditoría misma ya las rotó respecto al historial.
2. **El backend no está protegido contra fuerza bruta** en el login (sin límite de intentos): se omitió por el alcance académico, pero puede añadirse si se desea.
3. Los cambios están **stageados** (`git add -A`) para revisión con `git diff --cached`; no se hizo commit.
