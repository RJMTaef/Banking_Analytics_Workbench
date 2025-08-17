import duckdb, json
from pathlib import Path

DB_PATH = "data/warehouse/baw.duckdb"
OUT = Path("data/outputs"); OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(DB_PATH)

checks = {}
def q(name, sql):
    checks[name] = con.execute(sql).fetchone()[0]

q("customers_null_ids", "select count(*) from raw.customers where customer_id is null")
q("customers_duplicate_ids", "select count(*) - count(distinct customer_id) from raw.customers")
q("transactions_nulls", "select count(*) from raw.transactions where tx_id is null or customer_id is null or amount is null")
q("transactions_nonpositive", "select count(*) from raw.transactions where amount <= 0")

OUT.joinpath('data_quality_summary.json').write_text(json.dumps(checks, indent=2))
print(json.dumps(checks, indent=2))
