"""Limpia y valida el dataset de ventas de la ferretería.

Uso desde la raíz del proyecto:
    python python/clean_data.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "sales_data_ferreteria_10000.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "sales_data_clean.csv"
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "data_quality_report.json"

REQUIRED_COLUMNS = [
    "venta_id",
    "fecha",
    "hora",
    "cliente_id",
    "cliente",
    "tipo_cliente",
    "producto_id",
    "producto",
    "categoria",
    "subcategoria",
    "marca",
    "vendedor_id",
    "vendedor",
    "sucursal_id",
    "sucursal",
    "ciudad",
    "canal_venta",
    "medio_pago",
    "cantidad",
    "precio_unitario",
    "descuento_pct",
    "importe_bruto",
    "descuento_monto",
    "venta_neta",
    "costo_unitario",
    "costo_total",
    "utilidad",
    "margen_pct",
]

TEXT_COLUMNS = [
    "venta_id",
    "cliente_id",
    "cliente",
    "tipo_cliente",
    "producto_id",
    "producto",
    "categoria",
    "subcategoria",
    "marca",
    "vendedor_id",
    "vendedor",
    "sucursal_id",
    "sucursal",
    "ciudad",
    "canal_venta",
    "medio_pago",
]

NUMERIC_COLUMNS = [
    "cantidad",
    "precio_unitario",
    "descuento_pct",
    "importe_bruto",
    "descuento_monto",
    "venta_neta",
    "costo_unitario",
    "costo_total",
    "utilidad",
    "margen_pct",
]

MONEY_COLUMNS = [
    "precio_unitario",
    "importe_bruto",
    "descuento_monto",
    "venta_neta",
    "costo_unitario",
    "costo_total",
    "utilidad",
]

MONTH_NAMES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

WEEKDAY_NAMES = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Limpia el CSV de ventas y genera un reporte de calidad."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de entrada: {path}")

    data = pd.read_csv(path, encoding="utf-8-sig")
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(
            "Faltan columnas obligatorias: " + ", ".join(missing_columns)
        )
    return data


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    cleaned = data.copy()

    for column in TEXT_COLUMNS:
        cleaned[column] = cleaned[column].astype("string").str.strip()

    cleaned["fecha"] = pd.to_datetime(cleaned["fecha"], errors="raise")
    parsed_time = pd.to_datetime(cleaned["hora"], format="%H:%M:%S", errors="raise")
    cleaned["hora"] = parsed_time.dt.strftime("%H:%M:%S")

    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="raise")

    cleaned["cantidad"] = cleaned["cantidad"].astype("int64")
    cleaned[MONEY_COLUMNS] = cleaned[MONEY_COLUMNS].round(2)
    cleaned[["descuento_pct", "margen_pct"]] = cleaned[
        ["descuento_pct", "margen_pct"]
    ].round(4)

    cleaned["anio"] = cleaned["fecha"].dt.year.astype("int64")
    cleaned["mes_numero"] = cleaned["fecha"].dt.month.astype("int64")
    cleaned["mes"] = cleaned["mes_numero"].map(MONTH_NAMES)
    cleaned["trimestre"] = "T" + cleaned["fecha"].dt.quarter.astype(str)
    cleaned["dia_semana"] = cleaned["fecha"].dt.dayofweek.map(WEEKDAY_NAMES)

    cleaned = cleaned.sort_values(["fecha", "hora", "venta_id"]).reset_index(drop=True)
    return cleaned


def build_quality_report(data: pd.DataFrame) -> dict[str, object]:
    expected_gross = (data["cantidad"] * data["precio_unitario"]).round(2)
    expected_discount = (data["importe_bruto"] * data["descuento_pct"]).round(2)
    expected_net = (data["importe_bruto"] - data["descuento_monto"]).round(2)
    expected_cost = (data["cantidad"] * data["costo_unitario"]).round(2)
    expected_profit = (data["venta_neta"] - data["costo_total"]).round(2)

    checks = {
        "duplicate_sale_ids": int(data["venta_id"].duplicated().sum()),
        "rows_with_nulls": int(data.isna().any(axis=1).sum()),
        "invalid_quantities": int((data["cantidad"] <= 0).sum()),
        "negative_prices": int((data["precio_unitario"] < 0).sum()),
        "invalid_discounts": int(
            ((data["descuento_pct"] < 0) | (data["descuento_pct"] > 1)).sum()
        ),
        "invalid_margins": int(
            ((data["margen_pct"] < -1) | (data["margen_pct"] > 1)).sum()
        ),
        "gross_amount_mismatches": int(
            ((data["importe_bruto"] - expected_gross).abs() > 0.02).sum()
        ),
        "discount_amount_mismatches": int(
            ((data["descuento_monto"] - expected_discount).abs() > 0.02).sum()
        ),
        "net_sales_mismatches": int(
            ((data["venta_neta"] - expected_net).abs() > 0.02).sum()
        ),
        "total_cost_mismatches": int(
            ((data["costo_total"] - expected_cost).abs() > 0.02).sum()
        ),
        "profit_mismatches": int(
            ((data["utilidad"] - expected_profit).abs() > 0.02).sum()
        ),
    }

    return {
        "status": "PASS" if all(value == 0 for value in checks.values()) else "REVIEW",
        "row_count": int(len(data)),
        "column_count": int(len(data.columns)),
        "date_min": data["fecha"].min().date().isoformat(),
        "date_max": data["fecha"].max().date().isoformat(),
        "unique_customers": int(data["cliente_id"].nunique()),
        "unique_products": int(data["producto_id"].nunique()),
        "unique_sellers": int(data["vendedor_id"].nunique()),
        "unique_branches": int(data["sucursal_id"].nunique()),
        "checks": checks,
    }


def save_outputs(
    data: pd.DataFrame, report: dict[str, object], output_path: Path, report_path: Path
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    export_data = data.copy()
    export_data["fecha"] = export_data["fecha"].dt.strftime("%Y-%m-%d")
    export_data.to_csv(output_path, index=False, encoding="utf-8-sig")
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> None:
    args = parse_args()
    data = load_data(args.input)
    cleaned = clean_data(data)
    report = build_quality_report(cleaned)
    save_outputs(cleaned, report, args.output, args.report)

    print(f"Estado: {report['status']}")
    print(f"Filas procesadas: {report['row_count']:,}")
    print(f"CSV limpio: {args.output}")
    print(f"Reporte: {args.report}")

    if report["status"] != "PASS":
        raise SystemExit("La validación detectó incidencias. Revisa el reporte.")


if __name__ == "__main__":
    main()
