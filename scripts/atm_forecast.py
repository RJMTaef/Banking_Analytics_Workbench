import duckdb, pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pathlib import Path

DB_PATH = "data/warehouse/baw.duckdb"
OUT = Path("data/outputs"); OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(DB_PATH)

df = con.execute("select branch_id, date::date as d, cash_withdrawn from main_marts.fact_atm_demand order by branch_id, d").fetch_df()

forecasts=[]
for bid, g in df.groupby("branch_id"):
    g = g.set_index("d").asfreq("D").fillna(method="ffill")
    try:
        model = SARIMAX(g["cash_withdrawn"], order=(1,1,1), seasonal_order=(1,1,1,7), enforce_stationarity=False, enforce_invertibility=False)
        res = model.fit(disp=False)
        fc = res.get_forecast(steps=7).predicted_mean
        forecasts.append(pd.DataFrame({"branch_id": bid, "date": fc.index, "cash_forecast": fc.values}))
    except Exception:
        mean = g["cash_withdrawn"][-7:].mean()
        idx = pd.date_range(g.index[-1] + pd.Timedelta(days=1), periods=7, freq="D")
        forecasts.append(pd.DataFrame({"branch_id": bid, "date": idx, "cash_forecast": mean}))

out = pd.concat(forecasts, ignore_index=True)
out.to_parquet(OUT/"atm_forecast_7d.parquet", index=False)
print("Saved ATM forecasts -> data/outputs/atm_forecast_7d.parquet")
