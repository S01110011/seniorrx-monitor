"""Synthetic medication demand and inventory generation."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from medstock_optimizer.config import (
    DEFAULT_DEMAND_PATH,
    DEFAULT_INVENTORY_PATH,
    RANDOM_STATE,
    THERAPEUTIC_CLASSES,
)


def generate_medication_catalog(sku_count: int, seed: int = RANDOM_STATE) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    criticality = rng.choice(["routine", "important", "critical"], sku_count, p=[0.55, 0.32, 0.13])
    classes = rng.choice(THERAPEUTIC_CLASSES, sku_count)
    unit_cost = np.round(rng.lognormal(mean=3.1, sigma=0.75, size=sku_count), 2)
    lead_time_days = rng.integers(2, 15, sku_count)
    shelf_life_days = rng.integers(90, 900, sku_count)

    return pd.DataFrame(
        {
            "sku": [f"MED-{idx:04d}" for idx in range(1, sku_count + 1)],
            "medication_name": [f"{classes[idx]} {idx + 1:03d}" for idx in range(sku_count)],
            "therapeutic_class": classes,
            "criticality": criticality,
            "unit_cost": unit_cost,
            "lead_time_days": lead_time_days,
            "shelf_life_days": shelf_life_days,
        }
    )


def generate_daily_demand(
    days: int = 365, sku_count: int = 40, seed: int = RANDOM_STATE
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate synthetic daily medication demand and current inventory."""
    rng = np.random.default_rng(seed)
    catalog = generate_medication_catalog(sku_count=sku_count, seed=seed)
    dates = pd.date_range(end=pd.Timestamp("2026-05-26"), periods=days, freq="D")
    rows = []

    for item in catalog.itertuples(index=False):
        base_demand = rng.uniform(4, 95)
        if item.criticality == "critical":
            base_demand *= rng.uniform(0.35, 0.8)
        weekly_pattern = np.array([1.04, 1.02, 1.00, 1.03, 1.08, 0.82, 0.76])
        trend = rng.normal(0.0008, 0.0015)
        seasonality_strength = rng.uniform(0.03, 0.18)

        for day_index, date in enumerate(dates):
            weekday_factor = weekly_pattern[date.weekday()]
            seasonal_factor = 1 + seasonality_strength * np.sin(2 * np.pi * day_index / 90)
            expected = max(base_demand * weekday_factor * seasonal_factor * (1 + trend * day_index), 0.2)
            quantity = int(rng.poisson(expected))
            if rng.random() < 0.015:
                quantity = int(quantity * rng.uniform(1.8, 3.3))
            rows.append(
                {
                    "date": date.date().isoformat(),
                    "sku": item.sku,
                    "quantity_dispensed": quantity,
                }
            )

    demand = pd.DataFrame(rows)
    inventory = _generate_inventory_snapshot(catalog, demand, rng)
    return demand, inventory


def _generate_inventory_snapshot(
    catalog: pd.DataFrame, demand: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    recent = (
        demand.assign(date=pd.to_datetime(demand["date"]))
        .sort_values("date")
        .groupby("sku")
        .tail(30)
        .groupby("sku")["quantity_dispensed"]
        .mean()
        .rename("avg_recent_demand")
        .reset_index()
    )
    inventory = catalog.merge(recent, on="sku", how="left")
    inventory["on_hand_units"] = np.maximum(
        0,
        np.round(
            inventory["avg_recent_demand"]
            * inventory["lead_time_days"]
            * rng.uniform(0.45, 2.4, len(inventory))
        ),
    ).astype(int)
    inventory["on_order_units"] = np.round(
        inventory["avg_recent_demand"] * rng.uniform(0.0, 1.8, len(inventory))
    ).astype(int)
    inventory["minimum_order_quantity"] = np.maximum(
        5, np.round(inventory["avg_recent_demand"] * rng.uniform(1.0, 5.0, len(inventory)))
    ).astype(int)
    inventory["days_until_nearest_expiry"] = rng.integers(15, 540, len(inventory))
    return inventory.drop(columns=["avg_recent_demand"])


def save_synthetic_data(
    demand_out: Path,
    inventory_out: Path,
    days: int = 365,
    sku_count: int = 40,
    seed: int = RANDOM_STATE,
) -> tuple[Path, Path]:
    demand_out.parent.mkdir(parents=True, exist_ok=True)
    inventory_out.parent.mkdir(parents=True, exist_ok=True)
    demand, inventory = generate_daily_demand(days=days, sku_count=sku_count, seed=seed)
    demand.to_csv(demand_out, index=False)
    inventory.to_csv(inventory_out, index=False)
    return demand_out, inventory_out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic MedStock Optimizer data.")
    parser.add_argument("--demand-out", type=Path, default=DEFAULT_DEMAND_PATH)
    parser.add_argument("--inventory-out", type=Path, default=DEFAULT_INVENTORY_PATH)
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument("--sku-count", type=int, default=40)
    parser.add_argument("--seed", type=int, default=RANDOM_STATE)
    args = parser.parse_args()

    demand_path, inventory_path = save_synthetic_data(
        args.demand_out,
        args.inventory_out,
        days=args.days,
        sku_count=args.sku_count,
        seed=args.seed,
    )
    print(f"Saved demand data to {demand_path}")
    print(f"Saved inventory data to {inventory_path}")


if __name__ == "__main__":
    main()

