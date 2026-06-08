from medstock_optimizer.data import generate_daily_demand
from medstock_optimizer.forecasting import forecast_daily_demand, summarize_forecast


def test_forecast_daily_demand_returns_horizon_for_each_sku():
    demand, _ = generate_daily_demand(days=120, sku_count=5, seed=123)
    forecast = forecast_daily_demand(demand, horizon_days=14)

    assert len(forecast) == 5 * 14
    assert forecast["forecast_quantity"].ge(0).all()
    assert forecast["sku"].nunique() == 5


def test_summarize_forecast_returns_one_row_per_sku():
    demand, _ = generate_daily_demand(days=120, sku_count=4, seed=456)
    forecast = forecast_daily_demand(demand, horizon_days=7)
    summary = summarize_forecast(forecast)

    assert len(summary) == 4
    assert summary["forecast_daily_demand"].gt(0).all()

