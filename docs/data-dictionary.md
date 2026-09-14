# Diccionario de datos

Este documento se basa en `sql/01_schema.sql`, `sql/02_transform.sql`, el CSV original y la definición TMDL del modelo semántico. No describe campos ajenos a esas fuentes.

## Flujo de datos

El CSV original contiene 28 columnas. `python/clean_data.py` conserva esas columnas y agrega cinco atributos de calendario: `anio`, `mes_numero`, `mes`, `trimestre` y `dia_semana`. El cargador utiliza las 33 columnas resultantes para alimentar seis dimensiones y una tabla de hechos.

## Dataset de origen

| Campo | Tipo lógico | Descripción |
|---|---|---|
| `venta_id` | Texto | Identificador único de la venta. |
| `fecha` | Fecha | Fecha de la operación. |
| `hora` | Hora | Hora de la operación. |
| `cliente_id` | Texto | Identificador del cliente. |
| `cliente` | Texto | Nombre ficticio del cliente. |
| `tipo_cliente` | Texto | Clasificación del cliente. |
| `producto_id` | Texto | Identificador del producto. |
| `producto` | Texto | Nombre del producto. |
| `categoria` | Texto | Categoría comercial. |
| `subcategoria` | Texto | Subcategoría comercial. |
| `marca` | Texto | Marca del producto. |
| `vendedor_id` | Texto | Identificador del vendedor. |
| `vendedor` | Texto | Nombre ficticio del vendedor. |
| `sucursal_id` | Texto | Identificador de la sucursal. |
| `sucursal` | Texto | Nombre de la sucursal. |
| `ciudad` | Texto | Ciudad de la sucursal. |
| `canal_venta` | Texto | Canal utilizado para la venta. |
| `medio_pago` | Texto | Medio de pago. |
| `cantidad` | Entero | Unidades vendidas. |
| `precio_unitario` | Decimal | Precio por unidad antes del descuento. |
| `descuento_pct` | Decimal | Porcentaje de descuento expresado entre 0 y 1. |
| `importe_bruto` | Decimal | Cantidad multiplicada por precio unitario. |
| `descuento_monto` | Decimal | Importe monetario descontado. |
| `venta_neta` | Decimal | Importe bruto menos descuento. |
| `costo_unitario` | Decimal | Costo por unidad. |
| `costo_total` | Decimal | Cantidad multiplicada por costo unitario. |
| `utilidad` | Decimal | Venta neta menos costo total. |
| `margen_pct` | Decimal | Margen de la línea expresado entre 0 y 1. |

### Campos derivados por la limpieza

| Campo | Tipo lógico | Descripción |
|---|---|---|
| `anio` | Entero | Año de `fecha`. |
| `mes_numero` | Entero | Número de mes entre 1 y 12. |
| `mes` | Texto | Nombre del mes en español. |
| `trimestre` | Texto | Trimestre con formato `T1` a `T4`. |
| `dia_semana` | Texto | Nombre del día de la semana en español. |

## Modelo dimensional PostgreSQL

Todas las tablas pertenecen al esquema `bi_ferreteria`.

### `fact_ventas`

Grano: una fila por `venta_id` del dataset.

| Campo | Tipo PostgreSQL | Clave o regla | Descripción |
|---|---|---|---|
| `venta_key` | `BIGINT` | PK, identidad | Clave técnica de la tabla de hechos. |
| `venta_id` | `VARCHAR(20)` | Única, no nula | Identificador de negocio de la venta. |
| `fecha_key` | `DATE` | FK, no nula | Referencia a `dim_fecha`. |
| `hora` | `TIME` | No nula | Hora de la operación. |
| `cliente_id` | `VARCHAR(20)` | FK, no nula | Referencia a `dim_cliente`. |
| `producto_id` | `VARCHAR(20)` | FK, no nula | Referencia a `dim_producto`. |
| `vendedor_id` | `VARCHAR(20)` | FK, no nula | Referencia a `dim_vendedor`. |
| `sucursal_id` | `VARCHAR(20)` | FK, no nula | Referencia a `dim_sucursal`. |
| `canal_key` | `INTEGER` | FK, no nula | Referencia a `dim_canal`. |
| `cantidad` | `INTEGER` | Mayor que 0 | Unidades vendidas. |
| `precio_unitario` | `NUMERIC(12,2)` | Mayor o igual que 0 | Precio por unidad. |
| `descuento_pct` | `NUMERIC(7,4)` | Entre 0 y 1 | Porcentaje de descuento. |
| `importe_bruto` | `NUMERIC(14,2)` | No nulo | Importe antes del descuento. |
| `descuento_monto` | `NUMERIC(14,2)` | No nulo | Descuento monetario. |
| `venta_neta` | `NUMERIC(14,2)` | No nulo | Venta después del descuento. |
| `costo_unitario` | `NUMERIC(12,2)` | Mayor o igual que 0 | Costo por unidad. |
| `costo_total` | `NUMERIC(14,2)` | No nulo | Costo total de la línea. |
| `utilidad` | `NUMERIC(14,2)` | No nulo | Resultado de venta neta menos costo total. |
| `margen_pct` | `NUMERIC(7,4)` | No nulo | Margen porcentual de la línea. |

### `dim_fecha`

| Campo | Tipo PostgreSQL | Clave o regla | Descripción |
|---|---|---|---|
| `fecha_key` | `DATE` | PK | Fecha del calendario. |
| `anio` | `SMALLINT` | No nulo | Año. |
| `mes_numero` | `SMALLINT` | Entre 1 y 12 | Número utilizado para ordenar el mes. |
| `mes` | `VARCHAR(15)` | No nulo | Nombre del mes. |
| `trimestre` | `VARCHAR(2)` | No nulo | Trimestre. |
| `dia_semana` | `VARCHAR(10)` | No nulo | Día de la semana. |

### `dim_producto`

| Campo | Tipo PostgreSQL | Clave o regla | Descripción |
|---|---|---|---|
| `producto_id` | `VARCHAR(20)` | PK | Identificador del producto. |
| `producto` | `VARCHAR(150)` | No nulo | Nombre del producto. |
| `categoria` | `VARCHAR(100)` | No nulo | Categoría. |
| `subcategoria` | `VARCHAR(100)` | No nulo | Subcategoría. |
| `marca` | `VARCHAR(100)` | No nulo | Marca. |

### `dim_cliente`

| Campo | Tipo PostgreSQL | Clave o regla | Descripción |
|---|---|---|---|
| `cliente_id` | `VARCHAR(20)` | PK | Identificador del cliente. |
| `cliente` | `VARCHAR(150)` | No nulo | Nombre ficticio del cliente. |
| `tipo_cliente` | `VARCHAR(50)` | No nulo | Tipo de cliente. |

### `dim_sucursal`

| Campo | Tipo PostgreSQL | Clave o regla | Descripción |
|---|---|---|---|
| `sucursal_id` | `VARCHAR(20)` | PK | Identificador de la sucursal. |
| `sucursal` | `VARCHAR(100)` | No nulo | Nombre de la sucursal. |
| `ciudad` | `VARCHAR(100)` | No nulo | Ciudad. |

### `dim_canal`

| Campo | Tipo PostgreSQL | Clave o regla | Descripción |
|---|---|---|---|
| `canal_key` | `INTEGER` | PK, identidad | Clave técnica del canal. |
| `canal_venta` | `VARCHAR(50)` | No nulo | Canal comercial. |
| `medio_pago` | `VARCHAR(50)` | No nulo | Medio de pago. |

La combinación `canal_venta` y `medio_pago` es única.

### `dim_vendedor`

| Campo | Tipo PostgreSQL | Clave o regla | Descripción |
|---|---|---|---|
| `vendedor_id` | `VARCHAR(20)` | PK | Identificador del vendedor. |
| `vendedor` | `VARCHAR(150)` | No nulo | Nombre ficticio del vendedor. |

## Relaciones

`fact_ventas` se relaciona de muchos a uno con cada dimensión mediante `fecha_key`, `cliente_id`, `producto_id`, `vendedor_id`, `sucursal_id` y `canal_key`. El modelo semántico contiene seis relaciones activas.

## Vista de consulta

`bi_ferreteria.vw_ventas_powerbi` combina la tabla de hechos con las seis dimensiones y expone una vista plana con los campos descriptivos y métricos. Se utiliza para revisión y consultas; el modelo semántico mantiene las tablas dimensionales por separado.

## Medidas del modelo semántico

| Grupo | Medidas |
|---|---|
| Indicadores base | Ventas Netas, Importe Bruto, Costo Total, Utilidad Total, Descuento Total, Unidades Vendidas, Número de Ventas |
| Ratios | Ticket Promedio, Margen %, Descuento % |
| Inteligencia de tiempo | Ventas Año Anterior, Variación Ventas, Crecimiento Ventas %, Utilidad Año Anterior, Variación Utilidad, Crecimiento Utilidad %, Ventas YTD, Utilidad YTD |

## Volumen del dataset incluido

- Filas: 10 000.
- Fechas: 2024-01-01 a 2026-08-31.
- Clientes distintos por `cliente_id`: 401.
- Productos distintos: 56.
- Vendedores distintos: 15.
- Sucursales distintas: 6.

Todos los nombres y movimientos incluidos son ficticios.
