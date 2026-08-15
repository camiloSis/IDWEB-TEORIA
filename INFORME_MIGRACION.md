# Informe de Migración — MySQL → PostgreSQL

**Fecha:** 2026-08-08
**Documento guía:** DIAGNÓSTICO COMPLEMENTARIO — MIGRACIÓN DE MySQL A POSTGRESQL
**Base previa:** Informe de intervención de la auditoría (INFORME_INTERVENCION.md)

---

## 1. Archivos modificados

| Archivo | Cambio |
|---|---|
| `app.py` | Conexión de `mysql-connector-python` a `psycopg2`; configuración `POSTGRES_*`; consultas adaptadas (columna `fecha`); resto de la lógica (auth, validación, XSS) intacta |
| `requirements.txt` | `mysql-connector-python` → `psycopg2-binary` |
| `init.sql` | Reescrito en sintaxis PostgreSQL (SERIAL, `fecha`), sin `DROP`/`TRUNCATE`/`DELETE`, sin `CREATE DATABASE`; documentado como referencia de estructura |
| `docker-compose.yml` | Eliminados servicios `db` (MySQL) y `phpmyadmin`; queda solo `web`; conexión a PostgreSQL externo vía `host.docker.internal` + `extra_hosts` |
| `.env.example` | Variables `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` |
| `ESTRUCTURA.md` | Documenta PostgreSQL externo + pgAdmin 4, puerto 5432, host local vs Docker, `init.sql` como referencia |

## 2. Archivos creados

- Ninguno nuevo (`.env.example`, `.env` se actualizaron; `.env` no existe en el repo y está en `.gitignore`).

## 3. Archivos eliminados

- Ninguno (MySQL y phpMyAdmin solo se retiraron de `docker-compose.yml`; los contenedores huérfanos `mysql_db_individual` y `phpmyadmin_ui_individual` quedaron **detenidos**, no eliminados).

## 4. Cambios MySQL → PostgreSQL

- **Driver:** `mysql-connector-python` → `psycopg2-binary` (probado en Python 3.14 y 3.9-slim).
- **Conexión:** claves `host/user/password/database` → `host/port/database/user/password` con `POSTGRES_*`.
- **Queries:** INSERT idéntico (`%s` placeholders); SELECT ahora usa la columna **`fecha`** (estructura PostgreSQL existente) en vez de `fecha_envio` (MySQL).
- **`id`:** AUTO_INCREMENT → `SERIAL`.
- **Reintentos:** se conservaron (5 intentos, 2s).

## 5. Configuración

| Variable | Valor (documentado, sin secretos reales) |
|---|---|
| `POSTGRES_HOST` | `localhost` (local) / `host.docker.internal` (Docker) |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | `proyecto_db` |
| `POSTGRES_USER` | `postgres` (ejemplo) |
| `POSTGRES_PASSWORD` | `CHANGE_ME` (solo ejemplo) |

**Regla cumplida:** ninguna contraseña real en `app.py`, compose, Git o respuestas HTTP.

## 6. Pruebas EJECUTADAS

Contra el PostgreSQL **temporal descartable** (misma estructura `proyecto_db.public.mensajes_contacto` según `init.sql`, contenedor eliminado al terminar; **no tocó tu instancia** en `5432`):

- [x] Sintaxis Python (`py_compile`) OK
- [x] `psycopg2` importable (Python 3.14 local y 3.9-slim Docker) OK
- [x] `docker compose build` OK
- [x] Cero referencias a `mysql`/`mysql-connector`/`phpMyAdmin` en código y config
- [x] Página principal `GET /` → 200
- [x] POST `/submit_contact` "Prueba Migración" → 303, INSERT visible en `mensajes_contacto`
- [x] Datos recuperados por `/admin` (login correcto → tabla HTML con el mensaje)
- [x] XSS `<script>alert('XSS')</script>` → 0 scripts crudos; escapado `&lt;script&gt;`
- [x] `/admin` sin sesión → 303; login incorrecto → 401; logout → sesión invalidada
- [x] Respuesta 500 genérica sin excepciones internas y sin DB accesible

## 7. Pruebas PENDIENTES del usuario (contra tu PostgreSQL real)

1. Crear `.env` local (no se sube a Git) con tus credenciales.
2. Levantar: `docker compose up --build` (web) → http://localhost:5002
3. Enviar mensaje por el formulario y confirmar en pgAdmin 4:

```sql
SELECT * FROM mensajes_contacto ORDER BY fecha DESC;
```

4. `/admin/login` → `/admin` → ver mensaje.
5. Repetir prueba XSS y confirmar que se muestra como texto.

**Nota importante (sección 14 del diagnóstico):** tu PostgreSQL escucha solo en `127.0.0.1` (loopback). Dentro de Docker, `host.docker.internal` usa la IP `172.17.0.1:5432` y **la conexión fue rechazada** (`Connection refused`) porque no escucha en esa interfaz. Soluciones (debes elegir, es config de tu sistema):
- (a) ejecutar la app localmente (`python app.py`) — funciona contra `localhost:5432`; o
- (b) si quieres Docker, permitir que PostgreSQL escuche en `0.0.0.0` (pg_hba + listen_addresses) y abrir el puerto; **no lo modifiqué por tu cuenta**.

## 8. Base de datos

**No se modificó ni eliminó la base de datos existente** (`proyecto_db`); su tabla `mensajes_contacto` y datos quedaron intactos; la prueba E2E se hizo sobre un contenedor temporal ajeno al tuyo y se eliminó tras validar.

## 9. Problemas encontrados / decisiones

- **`host.docker.internal` → `connection refused`** en Docker: documentado arriba; requiere decidir (escuchar en 0.0.0.0 o ejecutar local).
- Contenedores viejos `mysql_db_individual`/`phpmyadmin_ui_individual` existen y están detenidos: ¿los elimino definitivamente?
- Sensibilidad: puedo probar contra tu instancia real si me autorizas y tengo `POSTGRES_PASSWORD` en `.env` local.
- MySQL ya no es necesario: verificado 0 referencias funcionales.