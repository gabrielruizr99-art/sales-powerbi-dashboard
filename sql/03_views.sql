CREATE OR REPLACE VIEW bi_ferreteria.vw_ventas_powerbi AS
SELECT
    f.venta_id,
    f.fecha_key AS fecha,
    f.hora,
    df.anio,
    df.mes_numero,
    df.mes,
    df.trimestre,
    df.dia_semana,
    dc.cliente_id,
    dc.cliente,
    dc.tipo_cliente,
    dp.producto_id,
    dp.producto,
    dp.categoria,
    dp.subcategoria,
    dp.marca,
    dv.vendedor_id,
    dv.vendedor,
    ds.sucursal_id,
    ds.sucursal,
    ds.ciudad,
    dca.canal_venta,
    dca.medio_pago,
    f.cantidad,
    f.precio_unitario,
    f.descuento_pct,
    f.importe_bruto,
    f.descuento_monto,
    f.venta_neta,
    f.costo_unitario,
    f.costo_total,
    f.utilidad,
    f.margen_pct
FROM bi_ferreteria.fact_ventas AS f
INNER JOIN bi_ferreteria.dim_fecha AS df ON df.fecha_key = f.fecha_key
INNER JOIN bi_ferreteria.dim_cliente AS dc ON dc.cliente_id = f.cliente_id
INNER JOIN bi_ferreteria.dim_producto AS dp ON dp.producto_id = f.producto_id
INNER JOIN bi_ferreteria.dim_vendedor AS dv ON dv.vendedor_id = f.vendedor_id
INNER JOIN bi_ferreteria.dim_sucursal AS ds ON ds.sucursal_id = f.sucursal_id
INNER JOIN bi_ferreteria.dim_canal AS dca ON dca.canal_key = f.canal_key;

