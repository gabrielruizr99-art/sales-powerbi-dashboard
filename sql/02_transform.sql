INSERT INTO bi_ferreteria.dim_fecha (
    fecha_key, anio, mes_numero, mes, trimestre, dia_semana
)
SELECT DISTINCT
    fecha::DATE,
    anio::SMALLINT,
    mes_numero::SMALLINT,
    mes,
    trimestre,
    dia_semana
FROM stg_ventas
ON CONFLICT (fecha_key) DO UPDATE SET
    anio = EXCLUDED.anio,
    mes_numero = EXCLUDED.mes_numero,
    mes = EXCLUDED.mes,
    trimestre = EXCLUDED.trimestre,
    dia_semana = EXCLUDED.dia_semana;

INSERT INTO bi_ferreteria.dim_cliente (cliente_id, cliente, tipo_cliente)
SELECT DISTINCT cliente_id, cliente, tipo_cliente
FROM stg_ventas
ON CONFLICT (cliente_id) DO UPDATE SET
    cliente = EXCLUDED.cliente,
    tipo_cliente = EXCLUDED.tipo_cliente;

INSERT INTO bi_ferreteria.dim_producto (
    producto_id, producto, categoria, subcategoria, marca
)
SELECT DISTINCT producto_id, producto, categoria, subcategoria, marca
FROM stg_ventas
ON CONFLICT (producto_id) DO UPDATE SET
    producto = EXCLUDED.producto,
    categoria = EXCLUDED.categoria,
    subcategoria = EXCLUDED.subcategoria,
    marca = EXCLUDED.marca;

INSERT INTO bi_ferreteria.dim_vendedor (vendedor_id, vendedor)
SELECT DISTINCT vendedor_id, vendedor
FROM stg_ventas
ON CONFLICT (vendedor_id) DO UPDATE SET
    vendedor = EXCLUDED.vendedor;

INSERT INTO bi_ferreteria.dim_sucursal (sucursal_id, sucursal, ciudad)
SELECT DISTINCT sucursal_id, sucursal, ciudad
FROM stg_ventas
ON CONFLICT (sucursal_id) DO UPDATE SET
    sucursal = EXCLUDED.sucursal,
    ciudad = EXCLUDED.ciudad;

INSERT INTO bi_ferreteria.dim_canal (canal_venta, medio_pago)
SELECT DISTINCT canal_venta, medio_pago
FROM stg_ventas
ON CONFLICT (canal_venta, medio_pago) DO NOTHING;

INSERT INTO bi_ferreteria.fact_ventas (
    venta_id, fecha_key, hora, cliente_id, producto_id, vendedor_id,
    sucursal_id, canal_key, cantidad, precio_unitario, descuento_pct,
    importe_bruto, descuento_monto, venta_neta, costo_unitario,
    costo_total, utilidad, margen_pct
)
SELECT
    s.venta_id,
    s.fecha::DATE,
    s.hora::TIME,
    s.cliente_id,
    s.producto_id,
    s.vendedor_id,
    s.sucursal_id,
    c.canal_key,
    s.cantidad::INTEGER,
    s.precio_unitario::NUMERIC(12, 2),
    s.descuento_pct::NUMERIC(7, 4),
    s.importe_bruto::NUMERIC(14, 2),
    s.descuento_monto::NUMERIC(14, 2),
    s.venta_neta::NUMERIC(14, 2),
    s.costo_unitario::NUMERIC(12, 2),
    s.costo_total::NUMERIC(14, 2),
    s.utilidad::NUMERIC(14, 2),
    s.margen_pct::NUMERIC(7, 4)
FROM stg_ventas AS s
INNER JOIN bi_ferreteria.dim_canal AS c
    ON c.canal_venta = s.canal_venta
   AND c.medio_pago = s.medio_pago
ON CONFLICT (venta_id) DO UPDATE SET
    fecha_key = EXCLUDED.fecha_key,
    hora = EXCLUDED.hora,
    cliente_id = EXCLUDED.cliente_id,
    producto_id = EXCLUDED.producto_id,
    vendedor_id = EXCLUDED.vendedor_id,
    sucursal_id = EXCLUDED.sucursal_id,
    canal_key = EXCLUDED.canal_key,
    cantidad = EXCLUDED.cantidad,
    precio_unitario = EXCLUDED.precio_unitario,
    descuento_pct = EXCLUDED.descuento_pct,
    importe_bruto = EXCLUDED.importe_bruto,
    descuento_monto = EXCLUDED.descuento_monto,
    venta_neta = EXCLUDED.venta_neta,
    costo_unitario = EXCLUDED.costo_unitario,
    costo_total = EXCLUDED.costo_total,
    utilidad = EXCLUDED.utilidad,
    margen_pct = EXCLUDED.margen_pct;
