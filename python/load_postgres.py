"""Carga el CSV limpio en el modelo dimensional de PostgreSQL.

Uso desde la raíz del proyecto:
    python python/load_postgres.py

La conexión se obtiene de PGHOST, PGPORT, PGDATABASE, PGUSER y PGPASSWORD.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import psycopg
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = PROJECT_ROOT / "data" / "processed" / "sales_data_clean.csv"
SQL_DIR = PROJECT_ROOT / "sql"

CSV_COLUMNS = [
    "venta_id", "fecha", "hora", "cliente_id", "cliente", "tipo_cliente",
    "producto_id", "producto", "categoria", "subcategoria", "marca",
    "vendedor_id", "vendedor", "sucursal_id", "sucursal", "ciudad",
    "canal_venta", "medio_pago", "cantidad", "precio_unitario",
    "descuento_pct", "importe_bruto", "descuento_monto", "venta_neta",
    "costo_unitario", "costo_total", "utilidad", "margen_pct", "anio",
    "mes_numero", "mes", "trimestre", "dia_semana",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Carga el CSV limpio en PostgreSQL sin duplicar ventas."
    )
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    return parser.parse_args()


def connection_parameters() -> dict[str, object]:
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "dbname": os.getenv("PGDATABASE", "sales_powerbi"),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD"),
    }


def read_sql(filename: str) -> str:
    return (SQL_DIR / filename).read_text(encoding="utf-8")


def create_staging_table(cursor: psycopg.Cursor[object]) -> None:
    fields = sql.SQL(",\n").join(
        sql.SQL("{} TEXT").format(sql.Identifier(column)) for column in CSV_COLUMNS
    )
    cursor.execute(
        sql.SQL("CREATE TEMP TABLE stg_ventas ({}) ON COMMIT DROP").format(fields)
    )


def copy_csv(cursor: psycopg.Cursor[object], csv_path: Path) -> None:
    columns = sql.SQL(", ").join(map(sql.Identifier, CSV_COLUMNS))
    statement = sql.SQL(
        "COPY stg_ventas ({}) FROM STDIN WITH "
        "(FORMAT CSV, HEADER TRUE, ENCODING 'UTF8')"
    ).format(columns)

    with csv_path.open("rb") as source, cursor.copy(statement) as copy:
        while chunk := source.read(1024 * 1024):
            copy.write(chunk)


def validate_source(csv_path: Path) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"No se encontró {csv_path}. Ejecuta primero python/clean_data.py."
        )
    if csv_path.stat().st_size == 0:
        raise ValueError(f"El archivo está vacío: {csv_path}")


def print_database_counts(cursor: psycopg.Cursor[object]) -> None:
    tables = [
        "dim_fecha", "dim_cliente", "dim_producto", "dim_vendedor",
        "dim_sucursal", "dim_canal", "fact_ventas",
    ]
    print("\nRegistros cargados:")
    for table in tables:
        cursor.execute(
            sql.SQL("SELECT COUNT(*) FROM bi_ferreteria.{}").format(
                sql.Identifier(table)
            )
        )
        count = cursor.fetchone()[0]
        print(f"  {table}: {count:,}")


def main() -> None:
    args = parse_args()
    validate_source(args.csv)
    params = connection_parameters()

    if not params["password"]:
        raise SystemExit("Falta PGPASSWORD. Configúralo antes de ejecutar la carga.")

    print(
        f"Conectando a {params['host']}:{params['port']}/{params['dbname']} "
        f"como {params['user']}..."
    )

    with psycopg.connect(**params) as connection:
        with connection.cursor() as cursor:
            cursor.execute(read_sql("01_schema.sql"))
            create_staging_table(cursor)
            copy_csv(cursor, args.csv)
            cursor.execute(read_sql("02_transform.sql"))
            cursor.execute(read_sql("03_views.sql"))
            print_database_counts(cursor)

    print("\nCarga completada correctamente.")


if __name__ == "__main__":
    main()

