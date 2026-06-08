from medstock_optimizer.data import save_synthetic_data
from medstock_optimizer.reporting import build_reports


def test_build_reports_creates_csv_and_excel_outputs(tmp_path):
    demand_path = tmp_path / "daily_demand.csv"
    inventory_path = tmp_path / "inventory.csv"
    report_dir = tmp_path / "reports"

    save_synthetic_data(demand_path, inventory_path, days=120, sku_count=5, seed=321)
    paths = build_reports(demand_path, inventory_path, report_dir, horizon_days=14)

    assert paths["replenishment_plan"].exists()
    assert paths["alerts"].exists()
    assert paths["forecast"].exists()
    assert paths["simulation"].exists()
    assert paths["excel"].exists()

