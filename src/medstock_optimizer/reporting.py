"""Reporting pipeline for MedStock Optimizer."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from medstock_optimizer.alerts import generate_alerts
from medstock_optimizer.config import DEFAULT_DEMAND_PATH, DEFAULT_INVENTORY_PATH, DEFAULT_REPORT_DIR
from medstock_optimizer.data import save_synthetic_data
from medstock_optimizer.forecasting import forecast_daily_demand, summarize_forecast
from medstock_optimizer.inventory import calculate_inventory_policy
from medstock_optimizer.simulation import simulate_replenishment


def load_or_generate_inputs(demand_path: Path, inventory_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not demand_path.exists() or not inventory_path.exists():
        save_synthetic_data(demand_path, inventory_path)
    demand = pd.read_csv(demand_path)
    inventory = pd.read_csv(inventory_path)
    return demand, inventory


def build_reports(
    demand_path: Path,
    inventory_path: Path,
    report_dir: Path,
    horizon_days: int = 28,
) -> dict[str, Path]:
    demand, inventory = load_or_generate_inputs(demand_path, inventory_path)
    forecast = forecast_daily_demand(demand, horizon_days=horizon_days)
    forecast_summary = summarize_forecast(forecast)
    policy = calculate_inventory_policy(inventory, forecast_summary)
    alerts = generate_alerts(policy)
    simulation = simulate_replenishment(policy, forecast, horizon_days=horizon_days)

    report_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "replenishment_plan": report_dir / "medstock_replenishment_plan.csv",
        "alerts": report_dir / "medstock_alerts.csv",
        "forecast": report_dir / "medstock_forecast.csv",
        "simulation": report_dir / "medstock_simulation.csv",
        "excel": report_dir / "medstock_optimizer_report.xlsx",
    }

    policy.to_csv(paths["replenishment_plan"], index=False)
    alerts.to_csv(paths["alerts"], index=False)
    forecast.to_csv(paths["forecast"], index=False)
    simulation.to_csv(paths["simulation"], index=False)
    _write_excel_report(paths["excel"], policy, alerts, forecast, simulation)
    return paths


def _write_excel_report(
    output_path: Path,
    policy: pd.DataFrame,
    alerts: pd.DataFrame,
    forecast: pd.DataFrame,
    simulation: pd.DataFrame,
) -> None:
    executive_summary = pd.DataFrame(
        [
            {"metric": "total_skus", "value": len(policy)},
            {"metric": "skus_to_order", "value": int((policy["recommended_order_units"] > 0).sum())},
            {"metric": "total_order_value", "value": round(float(policy["recommended_order_value"].sum()), 2)},
            {"metric": "alert_count", "value": len(alerts)},
            {"metric": "critical_alert_count", "value": int((alerts["severity"] == "high").sum())},
        ]
    )

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        executive_summary.to_excel(writer, sheet_name="Executive Summary", index=False)
        policy.to_excel(writer, sheet_name="Replenishment Plan", index=False)
        alerts.to_excel(writer, sheet_name="Alerts", index=False)
        forecast.to_excel(writer, sheet_name="Forecast", index=False)
        simulation.to_excel(writer, sheet_name="Simulation", index=False)

        for worksheet in writer.book.worksheets:
            worksheet.freeze_panes = "A2"
            for column_cells in worksheet.columns:
                max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 32)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run MedStock Optimizer reports.")
    parser.add_argument("--demand", type=Path, default=DEFAULT_DEMAND_PATH)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY_PATH)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--horizon-days", type=int, default=28)
    args = parser.parse_args()

    paths = build_reports(args.demand, args.inventory, args.report_dir, horizon_days=args.horizon_days)
    for name, path in paths.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()

