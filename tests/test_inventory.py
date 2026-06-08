from medstock_optimizer.data import generate_daily_demand
from medstock_optimizer.forecasting import forecast_daily_demand, summarize_forecast
from medstock_optimizer.inventory import calculate_inventory_policy


def test_calculate_inventory_policy_has_reorder_fields():
    demand, inventory = generate_daily_demand(days=120, sku_count=6, seed=789)
    forecast = forecast_daily_demand(demand, horizon_days=14)
    policy = calculate_inventory_policy(inventory, summarize_forecast(forecast))

    assert len(policy) == 6
    assert policy["safety_stock"].ge(0).all()
    assert policy["reorder_point"].ge(0).all()
    assert policy["recommended_order_units"].ge(0).all()
    assert policy["estimated_inventory_value"].ge(0).all()

