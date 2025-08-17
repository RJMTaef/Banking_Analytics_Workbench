import duckdb, os
from pathlib import Path

DB_PATH = "data/warehouse/baw.duckdb"
RAW_PATH = Path("data/raw"); RAW_PATH.mkdir(parents=True, exist_ok=True)
os.makedirs("data/warehouse", exist_ok=True)

con = duckdb.connect(DB_PATH)
for schema in ["raw","staging","marts","snapshots"]:
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")

def load_csv(table, filename):
    fp = (RAW_PATH/filename).as_posix()
    print(f"Loading {fp} -> raw.{table}")
    con.execute(f"DROP TABLE IF EXISTS raw.{table};")
    con.execute(f"""        CREATE TABLE raw.{table} AS
        SELECT * FROM read_csv_auto('{fp}', header=True, ignore_errors=True);
    """)

files = {
    "customers": "customers.csv",
    "accounts": "accounts.csv",
    "branches": "branches.csv",
    "transactions": "transactions.csv",
    "digital_sessions": "digital_sessions.csv",
    "support_tickets": "support_tickets.csv",
    "atm_withdrawals": "atm_withdrawals.csv"
}
for tbl, fn in files.items():
    load_csv(tbl, fn)

print(f"DuckDB database ready at {DB_PATH}")
