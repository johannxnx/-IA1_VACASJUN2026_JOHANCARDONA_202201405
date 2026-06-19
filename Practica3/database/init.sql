-- SmartInvoice - Script de creación de tablas
-- PostgreSQL 18

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) DEFAULT 'admin',
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de proveedores
CREATE TABLE IF NOT EXISTS proveedores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    nit VARCHAR(20) UNIQUE NOT NULL,
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(150),
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de facturas
CREATE TABLE IF NOT EXISTS facturas (
    id SERIAL PRIMARY KEY,
    proveedor_id INTEGER REFERENCES proveedores(id) ON DELETE SET NULL,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    numero_factura VARCHAR(50),
    fecha_factura DATE,
    subtotal NUMERIC(12,2),
    impuestos NUMERIC(12,2),
    total NUMERIC(12,2),
    archivo_nombre VARCHAR(255) NOT NULL,
    archivo_ruta VARCHAR(500) NOT NULL,
    archivo_tipo VARCHAR(10),
    nombre_proveedor_ocr VARCHAR(200),
    estado VARCHAR(20) DEFAULT 'Pendiente',
    datos_crudos TEXT,
    confianza_ocr NUMERIC(5,2),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    procesado_en TIMESTAMP
);

-- Tabla de bitácora
CREATE TABLE IF NOT EXISTS bitacora (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER REFERENCES facturas(id) ON DELETE SET NULL,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    documento VARCHAR(255),
    estado VARCHAR(20),
    resultado TEXT,
    accion VARCHAR(100),
    detalle_error TEXT
);

-- Tabla de reportes
CREATE TABLE IF NOT EXISTS reportes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    nombre VARCHAR(150) NOT NULL,
    tipo VARCHAR(10) NOT NULL,
    archivo_ruta VARCHAR(500) NOT NULL,
    enviado_email BOOLEAN DEFAULT FALSE,
    email_destino VARCHAR(150),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
