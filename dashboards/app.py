import streamlit as st
import duckdb, pandas as pd, numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------- Session / Page ----------------
st.set_page_config(page_title="Banking Analytics Workbench", layout="wide")

# keep theme state in a key that is NOT reused by a widget
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Dark"

def theme_tokens(mode: str):
    if mode == "Light":
        return dict(
            bg1="#f7f9fc", bg2="#eef2ff", spot1="#ffe3ec", spot2="#e7f3ff",
            text="#0f172a", muted="#334155", accent="#2563eb", accent2="#7c3aed",
            card_bg="rgba(255,255,255,0.76)", border="rgba(0,0,0,0.08)",
            plot_template="plotly_white", grid="rgba(120,120,120,.25)"
        )
    return dict(
        bg1="#0f1220", bg2="#0b1220", spot1="#182036", spot2="#2a1f49",
        text="#e8e9ff", muted="#b6bdd2", accent="#66a3ff", accent2="#9d6bff",
        card_bg="linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03))",
        border="rgba(255,255,255,.12)",
        plot_template="plotly_dark", grid="rgba(160,160,160,.22)"
    )

C = theme_tokens(st.session_state["theme_mode"])

# ---------------- Global CSS (Aurora + cards + icon) ----------------
st.markdown(f"""
<style>
/* animated aurora backdrop */
@keyframes aurora {{
  0% {{ background-position: 0% 50%; }}
  50% {{ background-position: 100% 50%; }}
  100% {{ background-position: 0% 50%; }}
}}
[data-testid="stAppViewContainer"] {{
  background:
    radial-gradient(900px 620px at 15% 10%, {C['spot2']} 0%, transparent 60%),
    radial-gradient(750px 520px at 85% 0%, {C['spot1']} 0%, transparent 55%),
    linear-gradient(120deg, {C['bg1']} 0%, {C['bg2']} 100%) !important;
}}
[data-testid="stAppViewContainer"]::before {{
  content:"";
  position: fixed; inset:-10%;
  background: conic-gradient(from 180deg at 50% 50%, {C['accent']}22, transparent, {C['accent2']}22, transparent);
  filter: blur(60px); z-index:-1; animation: aurora 18s ease-in-out infinite;
}}
.block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; }}

.title {{
  font-size: 44px; font-weight: 900; letter-spacing:.4px;
  background: linear-gradient(90deg, {C['accent']}, {C['accent2']});
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}}

.iconwrap button {{
  border:1px solid {C['border']}; background:{C['card_bg']};
  width:44px; height:44px; border-radius:999px;
  box-shadow:0 8px 28px rgba(0,0,0,.18); backdrop-filter:blur(10px);
}}
.iconwrap button p {{ margin:0; font-size:18px; }}

.card {{
  background:{C['card_bg']}; border:1px solid {C['border']};
  border-radius:18px; padding:18px 20px; transition: transform .15s ease, box-shadow .2s ease;
  box-shadow:0 10px 30px rgba(0,0,0,.15); backdrop-filter: blur(10px);
}}
.card:hover {{ transform: translateY(-2px); box-shadow:0 14px 36px rgba(0,0,0,.22); }}
.card h4 {{ margin:0; color:{C['muted']}; letter-spacing:.3px }}
.card .big {{ font-size:40px; font-weight:850; color:{C['text']}; margin-top:6px }}

hr {{ border:0; height:1px; background:linear-gradient(90deg,transparent,{C['grid']},transparent); }}
</style>
""", unsafe_allow_html=True)

# ---------------- Header with top-right icon toggle ----------------
left, right = st.columns([0.92, 0.08])
with left:
    st.markdown('<div class="title">Banking Analytics Workbench (BAW)</div>', unsafe_allow_html=True)
with right:
    st.markdown('<div class="iconwrap">', unsafe_allow_html=True)
    icon = "☀️" if st.session_state["theme_mode"] == "Dark" else "🌙"
    if st.button(icon, key="toggle_theme", help="Toggle theme", type="secondary"):
        st.session_state["theme_mode"] = "Light" if st.session_state["theme_mode"] == "Dark" else "Dark"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Data ----------------
con = duckdb.connect("data/warehouse/baw.duckdb")
con.execute("SET schema 'main_marts'")

n_customers = con.execute("select count(*) from dim_customer").fetchone()[0]
tx_7d = con.execute("""
  select coalesce(sum(amount),0)
  from fact_transactions
  where ts::date >= current_date - INTERVAL 7 DAY
""").fetchone()[0]

alerts = 0; churn_risk = 0.0
try:
    fraud = pd.read_parquet("data/outputs/fraud_scores.parquet")
    alerts = int((fraud["fraud_score"] > np.quantile(fraud["fraud_score"], 0.99)).sum())
except Exception:
    pass
try:
    churn = pd.read_parquet("data/outputs/churn_predictions.parquet")
    churn_risk = float((churn['churn_prob'] > 0.5).mean()*100)
except Exception:
    pass

# ---------------- KPIs ----------------
k1,k2,k3,k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="card"><h4>Customers</h4><div class="big">{n_customers:,}</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="card"><h4>Tx Volume (7d)</h4><div class="big">${tx_7d:,.0f}</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="card"><h4>High-Risk Alerts</h4><div class="big">{alerts:,}</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="card"><h4>Churn Risk &gt; 50%</h4><div class="big">{churn_risk:.1f}%</div></div>', unsafe_allow_html=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# ---------------- Time window control ----------------
tw_col1, tw_col2 = st.columns([0.8, 0.2])
with tw_col2:
    window = st.radio("Window", ["30d","60d","90d"], index=0, horizontal=True, label_visibility="collapsed")
win_days = int(window[:-1])

# ---------------- Volume line (readable in both modes) ----------------
st.subheader(f"Daily Transaction Volume (Last {win_days} Days)")
daily = con.execute(f"""
  select ts::date as d, sum(amount) as amt
  from fact_transactions
  where ts::date >= current_date - INTERVAL {win_days} DAY
  group by 1 order by 1
""").fetch_df()

fig_line = px.line(
    daily, x="d", y="amt", markers=True,
    labels={"d":"Date","amt":"Amount ($)"},
    color_discrete_sequence=[C["accent"]]
)
fig_line.update_traces(line=dict(width=3), marker=dict(size=6))
fig_line.update_layout(
    template=C["plot_template"], font=dict(color=C["text"]),
    xaxis=dict(title=None, tickfont=dict(color=C["text"]), gridcolor=C["grid"]),
    yaxis=dict(title=None, tickfont=dict(color=C["text"]), gridcolor=C["grid"]),
    margin=dict(l=0,r=10,t=10,b=0),
    hovermode="x unified",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    transition_duration=400
)
st.plotly_chart(fig_line, use_container_width=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# ---------------- 3D Surface ----------------
st.subheader("ATM Cash Forecast — 3D Surface (Next 7 Days)")
try:
    atm_fc = pd.read_parquet("data/outputs/atm_forecast_7d.parquet").copy()
    atm_fc["date"] = pd.to_datetime(atm_fc["date"])
    grid = atm_fc.pivot_table(index="branch_id", columns="date", values="cash_forecast", aggfunc="mean").sort_index()
    z = grid.values
    x = [d.strftime("%b %d") for d in grid.columns]
    y = grid.index.astype(int)

    surface = go.Figure(data=[go.Surface(z=z, x=x, y=y, colorscale="Viridis", opacity=0.96)])
    surface.update_layout(
        template=C["plot_template"], font=dict(color=C["text"]),
        scene=dict(
            xaxis_title="Date", yaxis_title="Branch ID", zaxis_title="Cash ($)",
            xaxis=dict(gridcolor=C["grid"], tickfont=dict(color=C["text"])),
            yaxis=dict(gridcolor=C["grid"], tickfont=dict(color=C["text"])),
            zaxis=dict(gridcolor=C["grid"], tickfont=dict(color=C["text"]))
        ),
        height=520, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(surface, use_container_width=True)
except Exception as e:
    st.info("Run `python scripts/atm_forecast.py` to generate forecasts.")
    st.caption(f"(Debug: {e})")

st.markdown("<hr/>", unsafe_allow_html=True)

# ---------------- Fraud table (futuristic styling) ----------------
st.subheader("Fraud Alerts — Top 50 (by score)")
try:
    tx = con.execute("select tx_id, customer_id, amount, ts from fact_transactions").fetch_df()
    fraud = pd.read_parquet("data/outputs/fraud_scores.parquet")
    top = (tx.merge(fraud, on=["customer_id","amount"], how="inner")
             .sort_values("fraud_score", ascending=False)
             .head(50)[["tx_id","customer_id","amount","ts","fraud_score"]])

    # risk tiers
    q90 = top["fraud_score"].quantile(0.90)
    q70 = top["fraud_score"].quantile(0.70)
    def tier(s):
        if s >= q90: return "🔴 High"
        if s >= q70: return "🟠 Medium"
        return "🟢 Low"
    top["risk_tier"] = top["fraud_score"].apply(tier)

    # ensure timestamp dtype for nicer rendering
    top["ts"] = pd.to_datetime(top["ts"])

    # column configs (currency, datetime, progress)
    max_score = float(top["fraud_score"].max() or 1.0)
    st.dataframe(
        top,
        hide_index=True,
        use_container_width=True,
        column_config={
            "tx_id": st.column_config.NumberColumn("TX ID"),
            "customer_id": st.column_config.NumberColumn("Customer"),
            "amount": st.column_config.NumberColumn("Amount", format="$%0.2f"),
            "ts": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm"),
            "fraud_score": st.column_config.ProgressColumn(
                "Risk Score", min_value=0.0, max_value=max_score, format="%0.3f"
            ),
            "risk_tier": st.column_config.TextColumn("Tier"),
        }
    )

    # download
    csv = top.to_csv(index=False).encode()
    st.download_button("Download alerts (CSV)", data=csv, file_name="fraud_alerts.csv",
                       mime="text/csv", type="secondary")
except Exception:
    st.caption("Run fraud scoring first: `python scripts/fraud_isoforest.py`.")
