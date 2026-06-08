# Data

This folder stores generated synthetic pharmacy demand and inventory files.

Generate data with:

```powershell
python -m medstock_optimizer.data --demand-out data/daily_demand.csv --inventory-out data/inventory.csv --days 365 --sku-count 40
```

Do not commit real medication transactions, patient-linked dispensing data or protected health information.

