"""Shared configuration for MedStock Optimizer."""

from pathlib import Path

RANDOM_STATE = 42
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DEMAND_PATH = PROJECT_ROOT / "data" / "daily_demand.csv"
DEFAULT_INVENTORY_PATH = PROJECT_ROOT / "data" / "inventory.csv"
DEFAULT_REPORT_DIR = PROJECT_ROOT / "reports"

SERVICE_LEVEL_Z = {
    "routine": 1.28,
    "important": 1.65,
    "critical": 2.05,
}

THERAPEUTIC_CLASSES = [
    "Antibiotic",
    "Analgesic",
    "Anticoagulant",
    "Antihypertensive",
    "Insulin",
    "Sedative",
    "Vasopressor",
    "Antiemetic",
]

