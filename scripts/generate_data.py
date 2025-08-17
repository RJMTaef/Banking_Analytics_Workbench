import numpy as np, pandas as pd, random
from pathlib import Path
from faker import Faker
from datetime import datetime, timedelta

BASE = Path("data"); RAW = BASE/"raw"
RAW.mkdir(parents=True, exist_ok=True)
np.random.seed(42); random.seed(42)
fake = Faker("en_CA")

PROVINCES = ["NS","NB","QC","ON","BC","AB","MB","SK","NL","PE","YT","NT","NU"]
CHANNELS = ["POS","ATM","E-TRANSFER","BILL","ONLINE"]
PRODUCTS = ["Chequing","Savings","CreditCard","Loan","Mortgage"]

N_CUSTOMERS = 3000
N_BRANCHES = 25

def gen_customers(n=N_CUSTOMERS):
    rows=[]; start_join = datetime.now() - timedelta(days=365*8)
    for cid in range(1, n+1):
        join_date = start_join + timedelta(days=int(np.random.gamma(2.0, 120)))
        rows.append({
            "customer_id": cid,
            "age": int(np.random.randint(18, 85)),
            "tenure_months": max(1, (datetime.now() - join_date).days // 30),
            "province": random.choice(PROVINCES),
            "risk_score": int(np.clip(np.random.normal(600, 80), 300, 850)),
            "join_date": join_date.date().isoformat()
        })
    return pd.DataFrame(rows)

def gen_accounts(customers: pd.DataFrame):
    rows=[]; aid=1
    for _, r in customers.iterrows():
        for _ in range(np.random.choice([1,1,2,2,3], p=[0.35,0.35,0.2,0.08,0.02])):
            rows.append({
                "account_id": aid,
                "customer_id": int(r.customer_id),
                "product_type": random.choice(PRODUCTS),
                "open_date": (datetime.fromisoformat(r.join_date) + timedelta(days=np.random.randint(0,180))).date().isoformat(),
                "status": random.choice(["Open","Open","Open","Dormant","Closed"])
            }); aid += 1
    return pd.DataFrame(rows)

def gen_branches(n=N_BRANCHES):
    rows=[]
    for bid in range(1, n+1):
        rows.append({
            "branch_id": bid,
            "name": f"Branch {bid}",
            "province": random.choice(PROVINCES),
            "lat": float(44.6 + np.random.normal(0, 0.8)),
            "lon": float(-63.6 + np.random.normal(0, 1.2))
        })
    return pd.DataFrame(rows)

def gen_transactions(customers, accounts, branches, days=150):
    rows=[]; txid=1; now = datetime.now()
    for _, c in customers.iterrows():
        k = np.random.poisson(90)
        cust_accts = accounts[accounts.customer_id==c.customer_id].account_id.values
        for _ in range(k):
            ts = now - timedelta(days=np.random.randint(0, days), hours=np.random.randint(0,24), minutes=np.random.randint(0,60))
            amount = round(np.random.lognormal(mean=3.2, sigma=0.8), 2)
            branch = int(np.random.randint(1, N_BRANCHES+1))
            rows.append({
                "tx_id": txid,
                "customer_id": int(c.customer_id),
                "account_id": int(np.random.choice(cust_accts)),
                "branch_id": branch,
                "amount": amount,
                "channel": random.choice(CHANNELS),
                "merchant_code": fake.bothify(text="M####"),
                "ts": ts.isoformat(sep=" ")
            }); txid += 1
    return pd.DataFrame(rows)

def gen_sessions(customers, days=90):
    rows=[]; sid=1; now = datetime.now()
    for _, c in customers.iterrows():
        k = np.random.poisson(20)
        for _ in range(k):
            start = now - timedelta(days=np.random.randint(0, days), hours=np.random.randint(0,24))
            dur = np.random.randint(30, 1800)
            rows.append({
                "session_id": sid,
                "customer_id": int(c.customer_id),
                "device_type": random.choice(["iOS","Android","Web"]),
                "start_ts": start.isoformat(sep=" "),
                "duration_s": int(dur),
                "events_count": int(np.random.randint(3, 50)),
                "conv_flag": int(np.random.choice([0,1], p=[0.85,0.15]))
            }); sid += 1
    return pd.DataFrame(rows)

def gen_tickets(customers, days=150):
    rows=[]; tid=1; now = datetime.now()
    for _, c in customers.iterrows():
        k = np.random.choice([0,0,0,1,1,2], p=[0.4,0.3,0.15,0.1,0.04,0.01])
        for _ in range(k):
            created = now - timedelta(days=np.random.randint(0, days), hours=np.random.randint(0,24))
            sla = int(np.random.choice([24, 48, 72], p=[0.6,0.3,0.1]))
            resolved = created + timedelta(hours=np.random.randint(1, max(2, sla+12)))
            rows.append({
                "ticket_id": tid,
                "customer_id": int(c.customer_id),
                "created_ts": created.isoformat(sep=" "),
                "category": random.choice(["Card","Online Banking","Branch","ATM","Other"]),
                "priority": random.choice(["Low","Medium","High"]),
                "sla_hours": sla,
                "resolved_ts": resolved.isoformat(sep=" "),
                "sentiment": random.choice(["neg","neu","pos"])
            }); tid += 1
    return pd.DataFrame(rows)

def gen_atm_withdrawals(branches, days=120):
    rows=[]; now = datetime.now().date()
    for _, b in branches.iterrows():
        base = np.random.randint(1500, 3500)
        for d in range(days):
            date = now - timedelta(days=d)
            seasonal = 1.0 + 0.1*np.sin(2*np.pi*(d/7.0))
            noise = np.random.normal(0, 120)
            cash = max(0, base*seasonal + noise)
            rows.append({
                "branch_id": int(b.branch_id),
                "date": date.isoformat(),
                "cash_withdrawn": round(cash,2),
                "withdrawals_cnt": int(max(0, np.random.normal(180, 30)))
            })
    return pd.DataFrame(rows)

def main():
    customers = gen_customers()
    accounts = gen_accounts(customers)
    branches = gen_branches()
    tx = gen_transactions(customers, accounts, branches)
    sessions = gen_sessions(customers)
    tickets = gen_tickets(customers)
    atm = gen_atm_withdrawals(branches)

    (RAW/'customers.csv').write_text(customers.to_csv(index=False))
    (RAW/'accounts.csv').write_text(accounts.to_csv(index=False))
    (RAW/'branches.csv').write_text(branches.to_csv(index=False))
    (RAW/'transactions.csv').write_text(tx.to_csv(index=False))
    (RAW/'digital_sessions.csv').write_text(sessions.to_csv(index=False))
    (RAW/'support_tickets.csv').write_text(tickets.to_csv(index=False))
    (RAW/'atm_withdrawals.csv').write_text(atm.to_csv(index=False))
    print("Generated raw CSVs in data/raw/")

if __name__ == "__main__":
    main()
