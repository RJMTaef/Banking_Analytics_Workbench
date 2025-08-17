import duckdb, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from pathlib import Path

DB_PATH = "data/warehouse/baw.duckdb"
OUT = Path("data/outputs"); OUT.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(DB_PATH)
# Use dbt's schema so we can reference tables without prefixes
con.execute("SET schema 'main_marts'")

# Build activity windows
df = con.execute("""
with t as (
  select customer_id, date_trunc('day', ts) as d, count(*) as tx_cnt
  from fact_transactions
  group by 1,2
),
agg as (
  select
    customer_id,
    sum(case when d >= current_date - INTERVAL 30 DAY then tx_cnt else 0 end) as tx_last_30,
    sum(case when d <  current_date - INTERVAL 30 DAY
              and d >= current_date - INTERVAL 120 DAY then tx_cnt else 0 end) as tx_prev_120
  from t
  group by 1
)
select * from agg
""").fetch_df()

# Primary label: "quiet recently, active historically"
df["churn_90d"] = ((df["tx_last_30"] <= 1) & (df["tx_prev_120"] >= 8)).astype(int)

# If still too few positives, relax thresholds progressively
pos = int(df["churn_90d"].sum())
if pos < 20:
    df["churn_90d"] = ((df["tx_last_30"] <= 2) & (df["tx_prev_120"] >= 6)).astype(int)
    pos = int(df["churn_90d"].sum())

# As a last resort, mark the bottom 10% by tx_last_30 as churn
if pos == 0:
    cutoff = df["tx_last_30"].quantile(0.10)
    df["churn_90d"] = (df["tx_last_30"] <= cutoff).astype(int)

# Bring in basic customer features
cust = con.execute("""
  select customer_id, age, tenure_months, risk_score
  from dim_customer
""").fetch_df()

X = df.merge(cust, on="customer_id", how="left").fillna(0)
y = X.pop("churn_90d")

# Guardrail: if by any chance still one class, print and skip training gracefully
if len(pd.unique(y)) < 2:
    print("Warning: only one class in churn labels; adjust thresholds or regenerate data.")
else:
    Xtr, Xte, ytr, yte = train_test_split(
        X.drop(columns=["customer_id"]), y, test_size=0.2, random_state=42, stratify=y
    )
    clf = LogisticRegression(max_iter=500).fit(Xtr, ytr)
    auc = roc_auc_score(yte, clf.predict_proba(Xte)[:,1])
    print(f"AUC={auc:.3f}")

    preds = clf.predict_proba(X.drop(columns=["customer_id"]))[:,1]
    out = pd.DataFrame({"customer_id": X["customer_id"], "churn_prob": preds})
    out.to_parquet(OUT/"churn_predictions.parquet", index=False)
    print("Saved churn predictions -> data/outputs/churn_predictions.parquet")
