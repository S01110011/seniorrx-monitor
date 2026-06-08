# MedStock Optimizer

MedStock Optimizer is a professional Python healthtech project for hospital pharmacy inventory planning.

It forecasts medication demand, calculates safety stock and reorder points, simulates replenishment decisions and exports operational reports in CSV and Excel.

## Hospital Challenge

Hospital pharmacies need to avoid both stockouts and excess inventory. Stockouts can interrupt care, while overstock increases waste, expiration losses and working capital pressure.

This project helps pharmacy and supply-chain teams answer:

- Which medications are at risk of stockout?
- Which items are overstocked?
- How much should be reordered?
- What is the projected inventory position over the next weeks?
- Which SKUs are high-priority due to criticality, lead time or volatile demand?

## Features

- Synthetic hospital medication demand generation
- Daily demand forecasting by medication SKU
- Safety stock and reorder point calculation
- Replenishment simulation with lead times
- Stockout, overstock and expiration-risk alerts
- Automated CSV and Excel reports
- Unit tests for forecasting, inventory policies and reporting
- GitHub Actions CI

## Project Structure

```text
medstock-optimizer/
├── data/
│   └── README.md
├── docs/
│   └── methodology.md
├── reports/
│   └── README.md
├── src/
│   └── medstock_optimizer/
│       ├── __init__.py
│       ├── alerts.py
│       ├── config.py
│       ├── data.py
│       ├── forecasting.py
│       ├── inventory.py
│       ├── reporting.py
│       └── simulation.py
├── tests/
│   ├── test_forecasting.py
│   ├── test_inventory.py
│   └── test_pipeline.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── pyproject.toml
└── README.md
```

## Quickstart

From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Generate synthetic pharmacy data:

```powershell
python -m medstock_optimizer.data --demand-out data/daily_demand.csv --inventory-out data/inventory.csv --days 365 --sku-count 40
```

Run optimization and export reports:

```powershell
python -m medstock_optimizer.reporting --demand data/daily_demand.csv --inventory data/inventory.csv --report-dir reports
```

Run tests and lint:

```powershell
python -m pytest
python -m ruff check .
```

## Outputs

The reporting command creates:

- `reports/medstock_replenishment_plan.csv`
- `reports/medstock_alerts.csv`
- `reports/medstock_forecast.csv`
- `reports/medstock_simulation.csv`
- `reports/medstock_optimizer_report.xlsx`

## Portfolio Note

The data is synthetic and safe for public GitHub. The project demonstrates Python engineering, forecasting, healthcare supply-chain reasoning and automated reporting.
