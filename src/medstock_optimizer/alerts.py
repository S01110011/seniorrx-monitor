"""Inventory alert generation."""

from __future__ import annotations

import pandas as pd


def generate_alerts(policy: pd.DataFrame) -> pd.DataFrame:
    """Generate action-oriented pharmacy inventory alerts."""
    rows = []
    for item in policy.itertuples(index=False):
        if item.days_of_supply <= item.lead_time_days:
            rows.append(_alert(item, "stockout_risk", "high", "Projected supply is below supplier lead time."))
        if item.inventory_position <= item.reorder_point:
            rows.append(_alert(item, "below_reorder_point", "medium", "Inventory position is below reorder point."))
        if item.days_of_supply >= 90 and item.criticality != "critical":
            rows.append(_alert(item, "overstock_risk", "medium", "Days of supply is above operating target."))
        if item.days_until_nearest_expiry <= max(item.days_of_supply, 1):
            rows.append(_alert(item, "expiration_risk", "medium", "Nearest expiry may occur before stock is consumed."))
        if item.criticality == "critical" and item.recommended_order_units > 0:
            rows.append(
                _alert(
                    item,
                    "critical_medication_priority",
                    "high",
                    "Critical medication requires replenishment review.",
                )
            )
    if not rows:
        return pd.DataFrame(columns=["sku", "medication_name", "alert_type", "severity", "message"])
    return pd.DataFrame(rows).sort_values(["severity", "sku"], ascending=[True, True])


def _alert(item: object, alert_type: str, severity: str, message: str) -> dict[str, str]:
    return {
        "sku": item.sku,
        "medication_name": item.medication_name,
        "alert_type": alert_type,
        "severity": severity,
        "message": message,
    }

