import duckdb, pandas as pd, numpy as np
from sklearn.ensemble import IsolationForest
from pathlib import Path

DB_PATH = "data/warehouse/baw.duckdb"
OUT = Path("data/outputs"); OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(DB_PATH)

tx = con.execute("""select customer_id, amount, ts
from main_marts.fact_transactions
""").fetch_df()

feat = tx.groupby("customer_id")["amount"].agg(["mean","std"]).rename(columns={"mean":"amt_mean","std":"amt_std"})
tx = tx.join(feat, on="customer_id")
tx["z"] = (tx["amount"] - tx["amt_mean"]) / tx["amt_std"].replace(0, 1)

X = tx[["amount","z"]].fillna(0).to_numpy()
clf = IsolationForest(contamination=0.01, random_state=42).fit(X)
tx["fraud_score"] = -clf.decision_function(X)

tx_out = tx[["customer_id","amount","z","fraud_score"]]
tx_out.to_parquet(OUT/"fraud_scores.parquet", index=False)
print("Saved fraud scores -> data/outputs/fraud_scores.parquet")
