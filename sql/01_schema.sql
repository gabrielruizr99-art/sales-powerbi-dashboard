CREATE SCHEMA IF NOT EXISTS bi_ferreteria;

CREATE TABLE IF NOT EXISTS bi_ferreteria.dim_fecha (
    fecha_key DATE PRIMARY KEY,
    anio SMALLINT NOT NULL,
    mes_numero SMALLINT NOT NULL CHECK (mes_numero BETWEEN 1 AND 12),
    mes VARCHAR(15) NOT NULL,
    trimestre VARCHAR(2) NOT NULL,
    dia_semana VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS bi_ferreteria.dim_cliente (
    cliente_id VARCHAR(20) PRIMARY KEY,
    cliente VARCHAR(150) NOT NULL,
    tipo_cliente VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS bi_ferreteria.dim_producto (
    producto_id VARCHAR(20) PRIMARY KEY,
    producto VARCHAR(150) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    subcategoria VARCHAR(100) NOT NULL,
    marca VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS bi_ferreteria.dim_vendedor (
    vendedor_id VARCHAR(20) PRIMARY KEY,
    vendedor VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS bi_ferreteria.dim_sucursal (
    sucursal_id VARCHAR(20) PRIMARY KEY,
    sucursal VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS bi_ferreteria.dim_canal (
    canal_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    canal_venta VARCHAR(50) NOT NULL,
    medio_pago VARCHAR(50) NOT NULL,
    CONSTRAINT uq_dim_canal UNIQUE (canal_venta, medio_pago)
);

CREATE TABLE IF NOT EXISTS bi_ferreteria.fact_ventas (
    venta_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    venta_id VARCHAR(20) NOT NULL UNIQUE,
    fecha_key DATE NOT NULL REFERENCES bi_ferreteria.dim_fecha (fecha_key),
    hora TIME NOT NULL,
    cliente_id VARCHAR(20) NOT NULL REFERENCES bi_ferreteria.dim_cliente (cliente_id),
    producto_id VARCHAR(20) NOT NULL REFERENCES bi_ferreteria.dim_producto (producto_id),
    vendedor_id VARCHAR(20) NOT NULL REFERENCES bi_ferreteria.dim_vendedor (vendedor_id),
    sucursal_id VARCHAR(20) NOT NULL REFERENCES bi_ferreteria.dim_sucursal (sucursal_id),
    canal_key INTEGER NOT NULL REFERENCES bi_ferreteria.dim_canal (canal_key),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(12, 2) NOT NULL CHECK (precio_unitario >= 0),
    descuento_pct NUMERIC(7, 4) NOT NULL CHECK (descuento_pct BETWEEN 0 AND 1),
    importe_bruto NUMERIC(14, 2) NOT NULL,
    descuento_monto NUMERIC(14, 2) NOT NULL,
    venta_neta NUMERIC(14, 2) NOT NULL,
    costo_unitario NUMERIC(12, 2) NOT NULL CHECK (costo_unitario >= 0),
    costo_total NUMERIC(14, 2) NOT NULL,
    utilidad NUMERIC(14, 2) NOT NULL,
    margen_pct NUMERIC(7, 4) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fact_ventas_fecha
    ON bi_ferreteria.fact_ventas (fecha_key);
CREATE INDEX IF NOT EXISTS idx_fact_ventas_cliente
    ON bi_ferreteria.fact_ventas (cliente_id);
CREATE INDEX IF NOT EXISTS idx_fact_ventas_producto
    ON bi_ferreteria.fact_ventas (producto_id);
CREATE INDEX IF NOT EXISTS idx_fact_ventas_vendedor
    ON bi_ferreteria.fact_ventas (vendedor_id);
CREATE INDEX IF NOT EXISTS idx_fact_ventas_sucursal
    ON bi_ferreteria.fact_ventas (sucursal_id);
CREATE INDEX IF NOT EXISTS idx_fact_ventas_canal
    ON bi_ferreteria.fact_ventas (canal_key);

