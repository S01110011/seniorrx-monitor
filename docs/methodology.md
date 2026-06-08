# Methodology

## Demand Forecasting

The project uses a robust weighted moving-average forecast. Recent demand receives more weight than older demand, and the model includes weekday adjustment so recurring hospital consumption patterns are reflected.

This approach is intentionally explainable for pharmacy operations teams. It can be extended with ARIMA, Prophet, gradient boosting or probabilistic forecasting.

## Safety Stock

Safety stock is estimated from demand variability during supplier lead time:

```text
safety_stock = service_level_z * demand_std * sqrt(lead_time_days)
```

Critical medications receive a higher service-level target.

## Reorder Point

```text
reorder_point = forecast_daily_demand * lead_time_days + safety_stock
```

## Recommended Order Quantity

The suggested order quantity covers projected demand for the lead time plus review period and safety stock, minus current on-hand and on-order inventory.

## Alerts

The project flags:

- `stockout_risk`
- `below_reorder_point`
- `overstock_risk`
- `expiration_risk`
- `critical_medication_priority`

## Production Extensions

- Connect to ERP/pharmacy systems
- Track lot-level expiration dates
- Add supplier reliability and partial fill rates
- Incorporate formulary substitutions
- Use probabilistic forecasts and scenario simulation
- Add approval workflows and audit logs

