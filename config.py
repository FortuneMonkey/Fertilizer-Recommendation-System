"""
Dashboard settings -- edit the paths below (or set the FERT_* environment variables).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Rules workbook (clones, dose rules, spacing, soils covered by the trial ...)
RULES_PATH = os.environ.get(
    "FERT_RULES_PATH", "rules/Fertilizer_Rules.xlsx")

# The cleaned soil database (use the file that already passed the quality check)
SOIL_DB_PATH = os.environ.get(
    "FERT_SOIL_DB_PATH", "data/Soil Sample Database.xlsx")
SOIL_DB_SHEET = 0                      # sheet name, or 0 = first sheet

# Where saved plans are stored (a small SQLite file, created automatically)
PLANS_DB_PATH = os.environ.get("FERT_PLANS_DB_PATH", str(BASE_DIR / "data" / "plans.db"))

APP_TITLE = "Fertilizer Recommendation"
DEFAULT_MAI_TARGET = 40
