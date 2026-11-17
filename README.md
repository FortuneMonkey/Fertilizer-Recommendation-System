# Fertilizer Recommendation Dashboard

Three pages: **Overview**, **Database**, **Recommendations**.

1. Database: filter the soil database and add compartments to a plan.
2. Recommendations: choose the clone, MAI target and spacing (3 × 2 or 3 × 2.5), then Calculate.
3. Save the plan (it is listed on the Overview) or download the doses as Excel.

## Set up (once)
1. Install Python packages: `pip install -r requirements.txt`
2. Open `config.py` and check the two paths:
   - `RULES_PATH`: the latest `Fertilizer_Rules.xlsx` (it must contain the **Spacing** sheet)
   - `SOIL_DB_PATH`: the cleaned soil database (use the file that passed the quality check)

## Run
Double-click `run_dashboard.bat`, or run `python -m streamlit run app.py` in this folder.
The dashboard opens in the browser (http://localhost:8501).

## Good to know
- All rules live in `Fertilizer_Rules.xlsx`: clones, dose rules, spacing, soils covered by the trial.
  After editing it, press **Reload data** on the Overview.
- After a new soil database export, run the converter and the quality check as before, then press **Reload data**.
- Saved plans are stored in `data/plans.db`. Back this file up if the plans matter.
- Only compartments in the covered soil (see the *Eligible Soils* sheet) can be added to a plan.

## Folder
- `app.py` start page and navigation
- `views/` the three pages
- `core/engine.py` the calculation (same engine as `fertilizer_recommendation.py`)
- `core/data.py`, `core/plans.py`, `core/session.py` data loading, saved plans, the plan in progress
- `core/ui.py` colours, spacing and reusable components (change the look here)
- `static/` the Inter font files and the icon (bundled, so no internet access is needed for fonts)
- `.streamlit/config.toml` theme and fonts
- `rules/Fertilizer_Rules.xlsx` copy of the rules workbook
