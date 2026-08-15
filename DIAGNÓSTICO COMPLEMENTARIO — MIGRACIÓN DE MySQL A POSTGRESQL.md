# DIAGNÓSTICO COMPLEMENTARIO — MIGRACIÓN DE MySQL A POSTGRESQL

**Proyecto:** IDWEB-TEORIA  
**Fase:** Migración de capa de persistencia  
**Fecha:** 2026-08-08  
**Documento complementario al diagnóstico formal de auditoría**

---

# 1. Propósito

Este documento complementa el diagnóstico de auditoría entregado anteriormente.

La auditoría original fue realizada considerando que el proyecto utilizaba:

```text
Python
   ↓
MySQL
   ↓
phpMyAdmin
```

Sin embargo, el entorno actual del proyecto ha cambiado.

La base de datos que debe utilizarse a partir de esta fase es:

```text
Python
   ↓
PostgreSQL
   ↓
pgAdmin 4
```

La migración debe realizarse **sin reconstruir innecesariamente el proyecto** y sin modificar la funcionalidad del frontend.

---

# 2. Estado actual confirmado

El usuario ya dispone de una instalación funcional de PostgreSQL administrada mediante pgAdmin 4.

La base de datos ya fue creada y comprobada manualmente.

## Base de datos

```text
proyecto_db
```

## Schema

```text
public
```

## Tabla

```text
mensajes_contacto
```

## Estructura confirmada

```text
id       SERIAL PRIMARY KEY
nombre   VARCHAR(100) NOT NULL
email    VARCHAR(100) NOT NULL
asunto   VARCHAR(200) NOT NULL
mensaje  TEXT NOT NULL
fecha    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
```

La base de datos funciona correctamente.

Por lo tanto, **el agente NO debe crear otra base de datos ni reemplazar la existente**.

---

# 3. Arquitectura objetivo

La arquitectura objetivo será:

```text
                    NAVEGADOR
                        │
                        ▼
              ┌──────────────────┐
              │     Frontend     │
              │ HTML / CSS / JS  │
              └────────┬─────────┘
                       │
                       │ POST
                       ▼
              ┌──────────────────┐
              │      app.py      │
              │ Python Backend   │
              └────────┬─────────┘
                       │
                       │ PostgreSQL
                       ▼
              ┌──────────────────┐
              │    PostgreSQL    │
              │                  │
              │   proyecto_db    │
              │        │         │
              │        ▼         │
              │ mensajes_contacto│
              └──────────────────┘
                       ▲
                       │
                administración
                       │
              ┌──────────────────┐
              │     pgAdmin 4    │
              │      Usuario     │
              └──────────────────┘
```

PostgreSQL será considerado un servicio **externo al proyecto**, administrado por el usuario.

---

# 4. Regla fundamental sobre PostgreSQL

El agente debe asumir que:

> **PostgreSQL ya está instalado, configurado y administrado por el usuario.**

Por tanto:

### El agente SÍ puede

- modificar `app.py`;
- cambiar el driver de base de datos;
- modificar `requirements.txt`;
- adaptar `init.sql`;
- modificar variables de configuración;
- modificar Docker para que la aplicación pueda conectarse a PostgreSQL;
- actualizar documentación;
- realizar pruebas de conexión si dispone del entorno necesario.

### El agente NO debe

- instalar otra instancia de MySQL;
- crear un contenedor MySQL;
- reemplazar PostgreSQL;
- eliminar PostgreSQL;
- eliminar `proyecto_db`;
- eliminar `mensajes_contacto`;
- modificar o borrar datos existentes;
- cambiar las credenciales reales;
- ejecutar comandos destructivos sobre la base de datos;
- recrear la base de datos innecesariamente.

---

# 5. Migración del driver Python

El proyecto actualmente utiliza:

```text
mysql-connector-python
```

Esta dependencia debe dejar de utilizarse para la conexión a la base de datos.

El agente debe seleccionar y configurar un driver PostgreSQL apropiado para Python.

La dependencia debe reflejarse correctamente en:

```text
requirements.txt
```

El agente debe eliminar:

```text
mysql-connector-python
```

si ya no existe ningún uso de MySQL en el proyecto.

No debe mantener simultáneamente dos drivers de base de datos sin una razón técnica justificada.

---

# 6. Modificación de `app.py`

El backend debe migrarse de MySQL a PostgreSQL.

Debe localizar y modificar:

- importaciones;
- creación de conexiones;
- parámetros de conexión;
- ejecución de consultas;
- manejo de errores;
- cierre de conexiones;
- cualquier código específico de MySQL.

El comportamiento funcional debe mantenerse.

El flujo debe continuar siendo:

```text
POST /submit_contact
        ↓
validación
        ↓
INSERT
        ↓
PostgreSQL
        ↓
mensajes_contacto
```

Y el panel administrativo debe continuar realizando:

```text
/admin
   ↓
SELECT
   ↓
mensajes_contacto
   ↓
mostrar resultados
```

---

# 7. Configuración mediante variables de entorno

Las credenciales de PostgreSQL NO deben quedar escritas directamente en `app.py`.

Utilizar variables de entorno.

Como referencia:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=proyecto_db
POSTGRES_USER=TU_USUARIO
POSTGRES_PASSWORD=TU_PASSWORD
```

Los nombres pueden modificarse si existe una convención mejor dentro del proyecto, pero deben ser coherentes.

---

# 8. `.env.example`

Crear o actualizar:

```text
.env.example
```

Debe contener únicamente valores de ejemplo.

Por ejemplo:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=proyecto_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_ME
```

**No introducir la contraseña real del usuario.**

---

# 9. `.env` y Git

El archivo:

```text
.env
```

debe estar incluido en:

```text
.gitignore
```

El agente no debe agregar credenciales reales al repositorio.

Debe comprobar que:

```text
.env
```

no sea incluido accidentalmente mediante Docker o Git.

---

# 10. `init.sql` — Adaptación a PostgreSQL

Este punto es obligatorio.

El archivo:

```text
init.sql
```

debe adaptarse para representar correctamente la estructura PostgreSQL del proyecto.

Debe dejar de contener sintaxis específica de MySQL.

La estructura debe corresponder a:

```sql
CREATE TABLE mensajes_contacto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    asunto VARCHAR(200) NOT NULL,
    mensaje TEXT NOT NULL,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

Si el agente considera técnicamente preferible utilizar:

```text
GENERATED ... AS IDENTITY
```

en lugar de `SERIAL`, puede hacerlo, pero debe mantener compatibilidad con el código y documentar el cambio.

---

# 11. Importante: `init.sql` NO debe recrear automáticamente la BD del usuario

Aunque `init.sql` debe ser adaptado a PostgreSQL, su función será principalmente:

- documentar la estructura;
- permitir reconstruir la tabla en un entorno nuevo;
- servir como referencia para el proyecto.

El agente **NO debe asumir que debe ejecutar automáticamente `init.sql` sobre la PostgreSQL del usuario**.

La base de datos:

```text
proyecto_db
```

ya existe.

La tabla:

```text
mensajes_contacto
```

ya existe.

Por tanto, no debe ejecutar automáticamente:

```sql
DROP DATABASE
```

ni:

```sql
DROP TABLE
```

ni comandos equivalentes.

Tampoco debe modificar la estructura existente si no es estrictamente necesario.

---

# 12. Compatibilidad entre `init.sql` y la BD existente

Después de adaptar `init.sql`, el agente debe comparar conceptualmente su estructura con la estructura actualmente existente:

```text
proyecto_db
└── public
    └── mensajes_contacto
```

Debe comprobar que sean equivalentes en:

- nombres;
- tipos;
- restricciones;
- clave primaria;
- valor por defecto de fecha;
- campos obligatorios.

Si detecta una diferencia, debe informarla antes de intentar modificar la BD existente.

---

# 13. Docker

La configuración anterior del proyecto contiene un servicio MySQL.

Esto ya no corresponde a la arquitectura actual.

El agente debe revisar:

```text
docker-compose.yml
```

y eliminar o adaptar la configuración relacionada exclusivamente con MySQL.

No debe crear un nuevo contenedor MySQL.

La aplicación debe conectarse a la instancia PostgreSQL que administra el usuario.

---

# 14. Conexión desde Docker a PostgreSQL

Existe una diferencia importante entre ejecutar el backend directamente en el sistema operativo y ejecutarlo dentro de Docker.

Si Python se ejecuta directamente en el sistema operativo:

```text
POSTGRES_HOST=localhost
```

puede ser correcto.

Si Python se ejecuta dentro de un contenedor:

```text
localhost
```

hace referencia al propio contenedor, no necesariamente al PostgreSQL del sistema anfitrión.

Por ello, el agente debe comprobar el entorno real de ejecución y configurar correctamente el host de PostgreSQL.

No debe asumir que `localhost` funcionará dentro del contenedor.

Si la solución requiere una configuración específica para Linux, debe documentarla claramente.

No modificar configuraciones del sistema operativo del usuario sin autorización.

---

# 15. Docker Compose

El agente debe revisar si el proyecto todavía necesita:

```text
db:
  image: mysql
```

La respuesta esperada es:

```text
NO
```

si PostgreSQL es externo.

El Compose final debería concentrarse en los servicios realmente utilizados por el proyecto.

No es obligatorio eliminar Docker completamente.

El objetivo es que:

```text
Docker → aplicación
```

y:

```text
PostgreSQL → servicio externo administrado por el usuario
```

puedan coexistir correctamente.

---

# 16. phpMyAdmin

El proyecto anteriormente utilizaba:

```text
phpMyAdmin
```

para administrar MySQL.

Como la base de datos actual es PostgreSQL y el usuario utiliza:

```text
pgAdmin 4
```

el servicio phpMyAdmin deja de ser necesario.

El agente debe eliminar del `docker-compose.yml` cualquier servicio de phpMyAdmin que exista exclusivamente para administrar el antiguo MySQL.

No debe intentar sustituir pgAdmin 4 por otra herramienta.

---

# 17. Flujo final del formulario

El comportamiento esperado es:

```text
Usuario
   │
   ▼
Formulario HTML
   │
   ▼
POST /submit_contact
   │
   ▼
app.py
   │
   ├── valida datos
   │
   ├── conecta a PostgreSQL
   │
   ├── INSERT INTO mensajes_contacto
   │
   └── confirma operación
   │
   ▼
PostgreSQL
   │
   ▼
proyecto_db.public.mensajes_contacto
```

El usuario NO necesita conocer la base de datos.

---

# 18. Flujo final del administrador

El administrador utilizará:

```text
/admin
```

pero el panel debe estar protegido por la autenticación corregida en la auditoría anterior.

Una vez autenticado:

```text
/admin
   │
   ▼
SELECT
   │
   ▼
PostgreSQL
   │
   ▼
mensajes_contacto
   │
   ▼
HTML escapado
   │
   ▼
Panel administrativo
```

Los mensajes no deben exponerse directamente desde PostgreSQL al navegador.

---

# 19. Prueba obligatoria de integración

Después de realizar la migración, el agente debe realizar una prueba de extremo a extremo.

Debe enviar un mensaje de prueba mediante el formulario.

Ejemplo:

```text
Nombre:
Prueba Migración

Email:
prueba@example.com

Asunto:
Prueba PostgreSQL

Mensaje:
Verificación de integración entre el formulario y PostgreSQL.
```

Debe comprobar:

```text
Formulario
   ↓
app.py
   ↓
PostgreSQL
   ↓
mensajes_contacto
```

Y confirmar que el registro aparece correctamente.

---

# 20. Verificación desde pgAdmin 4

El agente debe, cuando sea técnicamente posible, indicar el SQL que permite verificar el resultado:

```sql
SELECT *
FROM mensajes_contacto
ORDER BY fecha DESC;
```

El usuario debe poder ejecutar esta consulta desde pgAdmin 4.

Si el agente no tiene acceso a la instancia PostgreSQL del usuario, **no debe afirmar que la prueba fue realizada**.

Debe indicar:

```text
"No fue posible verificar la conexión real a PostgreSQL porque la instancia
es externa al entorno del agente."
```

---

# 21. Prueba de lectura desde `/admin`

Después de insertar el mensaje:

```text
Prueba Migración
```

el agente debe comprobar que:

```text
/admin
```

puede recuperarlo correctamente.

Debe verificarse simultáneamente:

```text
PostgreSQL → app.py → panel admin
```

---

# 22. Prueba de seguridad

Debe probarse nuevamente el escenario XSS de la auditoría anterior.

Enviar como mensaje:

```html
<script>alert('XSS')</script>
```

El resultado esperado es:

```text
<script>alert('XSS')</script>
```

mostrado como texto.

Nunca debe ejecutarse.

---

# 23. Dependencias finales esperadas

El agente debe revisar:

```text
requirements.txt
```

y asegurarse de que:

- el driver PostgreSQL necesario esté presente;
- el driver MySQL antiguo sea eliminado si ya no se utiliza;
- no existan dependencias innecesarias.

No agregar frameworks como Flask/FastAPI solamente para realizar esta migración.

Debe conservarse la arquitectura actual del backend salvo que exista una razón técnica explícita.

---

# 24. Documentación

Actualizar:

```text
ESTRUCTURA.md
```

para reflejar:

```text
Frontend
   ↓
Python backend
   ↓
PostgreSQL
   ↓
pgAdmin 4
```

Debe eliminarse cualquier afirmación que indique que la aplicación actual utiliza:

```text
MySQL
phpMyAdmin
mysql-connector-python
```

como parte de la arquitectura final.

También debe documentarse:

- nombre de la BD;
- nombre de la tabla;
- variables de entorno;
- puerto PostgreSQL esperado;
- diferencia entre ejecución local y Docker;
- que PostgreSQL es administrado externamente;
- que `init.sql` sirve como referencia/reconstrucción y no implica recrear automáticamente la BD existente.

---

# 25. Restricciones de seguridad

El agente debe cumplir:

```text
NO almacenar contraseña real en app.py
NO almacenar contraseña real en docker-compose.yml
NO almacenar contraseña real en Git
NO incluir .env en Git
NO imprimir contraseña en logs
NO mostrar contraseña en respuestas HTTP
NO modificar credenciales reales
```

---

# 26. Restricciones sobre datos existentes

El agente debe considerar la base de datos como:

```text
DATOS DEL USUARIO
```

Por tanto:

```text
DROP DATABASE             ❌
DROP TABLE                ❌
TRUNCATE mensajes_contacto ❌
DELETE datos existentes   ❌
ALTER destructivo         ❌
```

salvo autorización explícita del usuario.

La migración debe ser **no destructiva**.

---

# 27. Cambios esperados

## Debe modificar

```text
app.py
requirements.txt
docker-compose.yml
init.sql
ESTRUCTURA.md
```

según corresponda.

## Puede crear

```text
.env.example
.dockerignore
```

si todavía no existen.

## Puede eliminar

Configuraciones exclusivamente relacionadas con:

```text
MySQL
phpMyAdmin
```

si ya no son necesarias.

## No debe eliminar

```text
PostgreSQL
pgAdmin 4
proyecto_db
mensajes_contacto
```

ni datos existentes.

---

# 28. Criterios de aceptación

La migración será considerada correcta cuando:

- [ ] El proyecto ya no dependa de MySQL.
- [ ] El driver PostgreSQL esté correctamente configurado.
- [ ] `app.py` pueda conectarse a PostgreSQL.
- [ ] El formulario pueda insertar mensajes.
- [ ] Los mensajes aparezcan en `mensajes_contacto`.
- [ ] `/admin` pueda leer los mensajes.
- [ ] PostgreSQL continúe siendo administrado externamente.
- [ ] pgAdmin 4 pueda visualizar los registros.
- [ ] No existan credenciales hardcodeadas.
- [ ] `init.sql` sea válido para PostgreSQL.
- [ ] `init.sql` represente la estructura existente.
- [ ] `init.sql` no destruya ni recree automáticamente la BD del usuario.
- [ ] MySQL ya no sea necesario.
- [ ] phpMyAdmin ya no sea necesario.
- [ ] Docker no intente levantar MySQL.
- [ ] La página conserve su funcionamiento y diseño.
- [ ] El panel administrativo continúe protegido.
- [ ] El XSS continúe corregido.
- [ ] La documentación refleje PostgreSQL.

---

# 29. Qué debe informar el agente al finalizar

El agente debe entregar un informe final con:

### Archivos modificados

```text
...
```

### Archivos creados

```text
...
```

### Archivos eliminados

```text
...
```

### Cambios de MySQL → PostgreSQL

Explicar exactamente qué se cambió.

### Configuración

Indicar:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
```

sin revelar ninguna contraseña real.

### Pruebas

Indicar cuáles ejecutó realmente.

Separar:

```text
PRUEBAS EJECUTADAS
```

de:

```text
PRUEBAS QUE EL USUARIO DEBE REALIZAR
```

### Base de datos

Debe indicar expresamente:

```text
No se modificó/eliminó la base de datos existente.
```

si efectivamente fue así.

---

# 30. Instrucción directa para el agente

El siguiente bloque debe interpretarse como una extensión de la auditoría anterior:

```text
IMPORTANTE: ESTE DOCUMENTO ES UNA EXTENSIÓN DEL DIAGNÓSTICO ANTERIOR.

La auditoría original asumía que el proyecto conservaría MySQL.
Esa condición YA NO ES VÁLIDA.

El entorno actual utiliza PostgreSQL + pgAdmin 4.

MIGRA LA CAPA DE PERSISTENCIA DEL PROYECTO DE MYSQL A POSTGRESQL.

ESTADO CONFIRMADO:

- PostgreSQL ya está instalado y funcionando.
- El usuario administra PostgreSQL mediante pgAdmin 4.
- La base de datos "proyecto_db" ya existe.
- El schema utilizado es "public".
- La tabla "mensajes_contacto" ya existe.
- La tabla ya fue probada y funciona correctamente.
- NO debes crear otra base de datos.
- NO debes eliminar ni recrear la base de datos existente.
- NO debes eliminar ni modificar datos existentes.
- NO debes instalar ni levantar MySQL.
- NO debes mantener phpMyAdmin como administrador de esta base de datos.

ESTRUCTURA EXISTENTE:

proyecto_db
└── public
    └── mensajes_contacto

Columnas:

id       SERIAL PRIMARY KEY
nombre   VARCHAR(100) NOT NULL
email    VARCHAR(100) NOT NULL
asunto   VARCHAR(200) NOT NULL
mensaje  TEXT NOT NULL
fecha    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP

OBJETIVO:

Conseguir que:

formulario
    ↓
POST /submit_contact
    ↓
app.py
    ↓
PostgreSQL
    ↓
proyecto_db.public.mensajes_contacto

y que /admin pueda leer los mensajes almacenados.

CAMBIOS OBLIGATORIOS:

1. Reemplaza la conexión MySQL de app.py por PostgreSQL.

2. Reemplaza mysql-connector-python por un driver PostgreSQL adecuado.

3. Actualiza requirements.txt.

4. Adapta todas las consultas SQL que sean necesarias.

5. Utiliza variables de entorno para:
   POSTGRES_HOST
   POSTGRES_PORT
   POSTGRES_DB
   POSTGRES_USER
   POSTGRES_PASSWORD

6. Crea o actualiza .env.example.

7. Asegúrate de que .env esté incluido en .gitignore.

8. Adapta init.sql completamente a PostgreSQL.

9. IMPORTANTE SOBRE init.sql:
   - debe representar la estructura PostgreSQL actual;
   - debe servir como referencia para reconstruir la tabla en otro entorno;
   - NO debe ejecutarse automáticamente sobre la base de datos existente;
   - NO debe contener instrucciones destructivas;
   - NO debe hacer DROP DATABASE;
   - NO debe hacer DROP TABLE;
   - no debe asumir que la BD necesita ser creada nuevamente.

10. Revisa docker-compose.yml.

11. Elimina configuraciones y servicios exclusivamente relacionados con MySQL.

12. Elimina phpMyAdmin si solamente existía para administrar el antiguo MySQL.

13. NO crees un contenedor PostgreSQL salvo que exista una necesidad explícita.
    La PostgreSQL utilizada por este proyecto es la instancia externa
    administrada por el usuario mediante pgAdmin 4.

14. Comprueba cuidadosamente cómo se conectará el backend a PostgreSQL
    cuando se ejecute directamente y cuando se ejecute mediante Docker.

15. No asumas que "localhost" dentro de Docker equivale al host del sistema.

16. No cambies el frontend innecesariamente.

17. Mantén las correcciones de seguridad de la auditoría anterior:
    - autenticación administrativa;
    - protección contra XSS;
    - validación backend;
    - ausencia de credenciales hardcodeadas;
    - protección de archivos privados.

18. No migres a Flask, FastAPI, Node.js, React u otro framework.

19. No cambies PostgreSQL por otra base de datos.

20. No modifiques ni borres datos existentes.

ANTES DE MODIFICAR:

Inspecciona primero:

- app.py
- requirements.txt
- init.sql
- docker-compose.yml
- Dockerfile
- ESTRUCTURA.md
- .gitignore
- cualquier archivo relacionado con MySQL.

Después explica brevemente qué partes deben cambiar.

DESPUÉS DE MODIFICAR:

Comprueba sintaxis Python.

Comprueba dependencias.

Comprueba Docker si corresponde.

Comprueba que no queden referencias funcionales a MySQL.

Comprueba que no queden referencias innecesarias a phpMyAdmin.

Comprueba que init.sql sea sintácticamente válido para PostgreSQL.

Comprueba que la estructura descrita por init.sql coincida con:

proyecto_db.public.mensajes_contacto

Si tienes acceso real a PostgreSQL, realiza una prueba de inserción y lectura.

Si NO tienes acceso a la instancia PostgreSQL del usuario, NO afirmes que probaste la conexión real.

En ese caso, indica claramente qué debe probar el usuario desde su entorno.

PRUEBA FINAL ESPERADA:

Enviar un mensaje desde el formulario.

Comprobar que llega a:

proyecto_db.public.mensajes_contacto

Después acceder al panel /admin y comprobar que el mensaje aparece.

También realizar la prueba XSS:

<script>alert('XSS')</script>

y comprobar que se muestra como texto y NO se ejecuta.

REGLA FINAL:

No reconstruyas el proyecto.

No hagas una migración tecnológica innecesaria.

No alteres el diseño.

No elimines contenido personal.

No borres datos.

No inventes credenciales.

No declares una prueba exitosa si realmente no fue ejecutada.

Al finalizar entrega un informe con:

- archivos modificados;
- archivos creados;
- archivos eliminados;
- cambios realizados;
- cambios MySQL → PostgreSQL;
- pruebas realmente ejecutadas;
- pruebas pendientes que debe realizar el usuario;
- problemas encontrados;
- decisiones que requieran aprobación del usuario.
```

---

# 31. Resultado esperado de esta fase

Al finalizar esta intervención, el proyecto debería haber pasado de:

```text
IDWEB-TEORIA
│
├── Python
├── MySQL
├── phpMyAdmin
└── Docker
```

a:

```text
IDWEB-TEORIA
│
├── Frontend
├── Python Backend
├── Docker
│
└── PostgreSQL externo
        │
        ├── proyecto_db
        │     └── mensajes_contacto
        │
        └── administrado mediante pgAdmin 4
```

La responsabilidad queda claramente separada:

**Agente IA:**

```text
Código
Configuración
Migración MySQL → PostgreSQL
Docker
Documentación
Pruebas técnicas
```

**Tú:**

```text
PostgreSQL
pgAdmin 4
Credenciales
Base de datos
Datos almacenados
Aprobación final
```

Y lo más importante: **el agente no debe tocar destructivamente tu PostgreSQL existente**. Su trabajo consiste en adaptar el proyecto para que utilice correctamente la infraestructura que tú ya preparaste.