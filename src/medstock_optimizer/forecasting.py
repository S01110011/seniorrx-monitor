"""Demand forecasting for medication SKUs."""

from __future__ import annotations

import numpy as np
import pandas as pd


def prepare_demand(demand: pd.DataFrame) -> pd.DataFrame:
    prepared = demand.copy()
    prepared["date"] = pd.to_datetime(prepared["date"])
    prepared["quantity_dispensed"] = prepared["quantity_dispensed"].clip(lower=0)
    return prepared.sort_values(["sku", "date"])


def forecast_daily_demand(
    demand: pd.DataFrame,
    horizon_days: int = 28,
    lookback_days: int = 90,
) -> pd.DataFrame:
    """Forecast daily demand per SKU using weighted moving averages and weekday factors."""
    prepared = prepare_demand(demand)
    max_date = prepared["date"].max()
    forecast_dates = pd.date_range(max_date + pd.Timedelta(days=1), periods=horizon_days, freq="D")
    rows = []

    for sku, group in prepared.groupby("sku"):
        recent = group[group["date"] > max_date - pd.Timedelta(days=lookback_days)].copy()
        if recent.empty:
            recent = group.copy()
        recent["age"] = (max_date - recent["date"]).dt.days
        recent["weight"] = np.exp(-recent["age"] / max(lookback_days / 3, 1))
        baseline = float(np.average(recent["quantity_dispensed"], weights=recent["weight"]))
        demand_std = float(recent["quantity_dispensed"].std(ddof=0))
        weekday_avg = recent.groupby(recent["date"].dt.weekday)["quantity_dispensed"].mean()
        overall_avg = max(float(recent["quantity_dispensed"].mean()), 0.1)

        for forecast_date in forecast_dates:
            weekday_factor = float(weekday_avg.get(forecast_date.weekday(), overall_avg) / overall_avg)
            forecast_qty = max(baseline * weekday_factor, 0.0)
            rows.append(
                {
                    "date": forecast_date.date().isoformat(),
                    "sku": sku,
                    "forecast_quantity": round(forecast_qty, 2),
                    "demand_std": round(demand_std, 2),
                    "method": "weighted_moving_average_weekday_adjusted",
                }
            )

    return pd.DataFrame(rows)


def summarize_forecast(forecast: pd.DataFrame) -> pd.DataFrame:
    return (
        forecast.groupby("sku")
        .agg(
            forecast_daily_demand=("forecast_quantity", "mean"),
            forecast_period_demand=("forecast_quantity", "sum"),
            demand_std=("demand_std", "mean"),
        )
        .reset_index()
    )

