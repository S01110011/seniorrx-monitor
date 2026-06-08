"""Inventory replenishment simulation."""

from __future__ import annotations

import pandas as pd


def simulate_replenishment(
    policy: pd.DataFrame,
    forecast: pd.DataFrame,
    horizon_days: int = 28,
) -> pd.DataFrame:
    """Simulate daily projected inventory after recommended replenishment decisions."""
    forecast = forecast.copy()
    forecast["date"] = pd.to_datetime(forecast["date"])
    rows = []

    for item in policy.itertuples(index=False):
        sku_forecast = forecast[forecast["sku"] == item.sku].sort_values("date").head(horizon_days)
        on_hand = float(item.on_hand_units)
        pending_receipt_day = int(item.lead_time_days)
        stockout_days = 0

        for day_index, row in enumerate(sku_forecast.itertuples(index=False), start=1):
            if day_index == pending_receipt_day and item.recommended_order_units > 0:
                on_hand += float(item.recommended_order_units)
            on_hand -= float(row.forecast_quantity)
            if on_hand < 0:
                stockout_days += 1
                on_hand = 0
            rows.append(
                {
                    "date": row.date.date().isoformat(),
                    "sku": item.sku,
                    "projected_on_hand_units": round(on_hand, 2),
                    "recommended_order_units": item.recommended_order_units,
                    "stockout_days_to_date": stockout_days,
                }
            )

    return pd.DataFrame(rows)

