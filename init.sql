-- ============================================
-- ESTRUCTURA DE REFERENCIA PARA POSTGRESQL
-- ============================================
-- La instancia PostgreSQL es externa y administrada por el usuario
-- mediante pgAdmin 4. La base de datos "proyecto_db" y la tabla
-- "mensajes_contacto" ya existen y NO deben recrearse.
--
-- Este archivo sirve como documentación y referencia para reconstruir
-- la estructura en un entorno nuevo. No contiene instrucciones
-- destructivas (no usa DROP, TRUNCATE ni DELETE).
--
-- Estructura existente:
--   proyecto_db.public.mensajes_contacto
-- ============================================

CREATE TABLE IF NOT EXISTS mensajes_contacto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    asunto VARCHAR(200) NOT NULL,
    mensaje TEXT NOT NULL,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);