"""Inventory policy calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd

from medstock_optimizer.config import SERVICE_LEVEL_Z


def calculate_inventory_policy(
    inventory: pd.DataFrame,
    forecast_summary: pd.DataFrame,
    review_period_days: int = 14,
) -> pd.DataFrame:
    """Calculate safety stock, reorder points and recommended order quantities."""
    policy = inventory.merge(forecast_summary, on="sku", how="left")
    policy["forecast_daily_demand"] = policy["forecast_daily_demand"].fillna(0)
    policy["demand_std"] = policy["demand_std"].fillna(0)
    policy["service_level_z"] = policy["criticality"].map(SERVICE_LEVEL_Z).fillna(1.28)
    policy["safety_stock"] = np.ceil(
        policy["service_level_z"] * policy["demand_std"] * np.sqrt(policy["lead_time_days"])
    ).astype(int)
    policy["reorder_point"] = np.ceil(
        policy["forecast_daily_demand"] * policy["lead_time_days"] + policy["safety_stock"]
    ).astype(int)
    policy["target_stock"] = np.ceil(
        policy["forecast_daily_demand"] * (policy["lead_time_days"] + review_period_days)
        + policy["safety_stock"]
    ).astype(int)
    policy["inventory_position"] = policy["on_hand_units"] + policy["on_order_units"]
    policy["raw_order_quantity"] = policy["target_stock"] - policy["inventory_position"]
    policy["recommended_order_units"] = np.where(
        policy["raw_order_quantity"] > 0,
        np.maximum(policy["raw_order_quantity"], policy["minimum_order_quantity"]),
        0,
    ).astype(int)
    policy["days_of_supply"] = np.where(
        policy["forecast_daily_demand"] > 0,
        policy["on_hand_units"] / policy["forecast_daily_demand"],
        np.inf,
    )
    policy["estimated_inventory_value"] = (
        policy["on_hand_units"] * policy["unit_cost"]
    ).round(2)
    policy["recommended_order_value"] = (
        policy["recommended_order_units"] * policy["unit_cost"]
    ).round(2)
    return policy.drop(columns=["raw_order_quantity"])

