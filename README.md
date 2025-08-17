# Banking Analytics Workbench (BAW)

An end-to-end **local** retail-banking analytics platform on synthetic data:
ingest → DuckDB warehouse → dbt models → data quality → ML (fraud, churn, ATM demand) → Streamlit dashboard.

## Quick Start
```bash
cd rbc-baw
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt

# Point dbt to the local profiles
# macOS/Linux:
export DBT_PROFILES_DIR=$(pwd)/.dbt
# Windows PowerShell:
# $env:DBT_PROFILES_DIR="$PWD/.dbt"

# Generate data → load → transform
python scripts/generate_data.py
python scripts/load_to_duckdb.py
dbt deps && dbt run && dbt test

# Run ML modules
python scripts/fraud_isoforest.py
python scripts/churn_baseline.py
python scripts/atm_forecast.py

# Dashboard
streamlit run dashboards/app.py
```
