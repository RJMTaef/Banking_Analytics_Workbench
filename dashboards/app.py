import streamlit as st
import duckdb, pandas as pd, numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------- Session / Page ----------------
st.set_page_config(page_title="Banking Analytics Workbench", layout="wide", initial_sidebar_state="collapsed")

# keep theme state in a key that is NOT reused by a widget
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Dark"

def theme_tokens(mode: str):
    if mode == "Light":
        return dict(
            bg1="#f7f9fc", bg2="#eef2ff", spot1="#ffe3ec", spot2="#e7f3ff",
            text="#0f172a", muted="#334155", accent="#2563eb", accent2="#7c3aed",
            card_bg="rgba(255,255,255,0.92)", border="rgba(0,0,0,0.08)",
            plot_template="plotly_white", grid="rgba(120,120,120,.25)",
            success="#10b981", warning="#f59e0b", danger="#ef4444"
        )
    return dict(
        bg1="#0f1220", bg2="#0b1220", spot1="#182036", spot2="#2a1f49",
        text="#e8e9ff", muted="#b6bdd2", accent="#66a3ff", accent2="#9d6bff",
        card_bg="linear-gradient(180deg, rgba(255,255,255,.12), rgba(255,255,255,.06))",
        border="rgba(255,255,255,.16)",
        plot_template="plotly_dark", grid="rgba(160,160,160,.22)",
        success="#34d399", warning="#fbbf24", danger="#f87171"
    )

C = theme_tokens(st.session_state["theme_mode"])

# ---------------- Enhanced Global CSS ----------------
st.markdown(f"""
<style>
/* Enhanced animated aurora backdrop */
@keyframes aurora {{
  0% {{ background-position: 0% 50%; }}
  50% {{ background-position: 100% 50%; }}
  100% {{ background-position: 0% 50%; }}
}}

@keyframes float {{
  0%, 100% {{ transform: translateY(0px); }}
  50% {{ transform: translateY(-10px); }}
}}

@keyframes pulse {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.7; }}
}}

@keyframes shimmer {{
  0% {{ transform: translateX(-100%); }}
  100% {{ transform: translateX(100%); }}
}}

@keyframes glow {{
  0%, 100% {{ box-shadow: 0 0 20px {C['accent']}40; }}
  50% {{ box-shadow: 0 0 40px {C['accent']}80, 0 0 60px {C['accent']}40; }}
}}

@keyframes slideIn {{
  from {{ transform: translateY(30px); opacity: 0; }}
  to {{ transform: translateY(0); opacity: 1; }}
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

.block-container {{ 
  padding-top: 1.5rem; 
  padding-bottom: 2.5rem; 
  max-width: 1400px;
}}

/* Enhanced title with subtle glow and one-time animation */
.title {{
  font-size: 52px; 
  font-weight: 900; 
  letter-spacing:.6px;
  background: linear-gradient(90deg, {C['accent']}, {C['accent2']}, {C['accent']}, {C['accent2']});
  background-size: 300% 300%;
  -webkit-background-clip:text; 
  -webkit-text-fill-color:transparent;
  animation: slideIn 1s ease-out;
  text-align: center;
  margin-bottom: 1rem;
  text-shadow: 0 0 20px {C['accent']}30;
  position: relative;
}}

.title::after {{
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 3px;
  background: linear-gradient(90deg, {C['accent']}, {C['accent2']});
  border-radius: 2px;
}}

.subtitle {{
  font-size: 20px;
  color: {C['muted']};
  text-align: center;
  margin-bottom: 2.5rem;
  font-weight: 300;
  animation: slideIn 1s ease-out;
  opacity: 0.9;
}}

/* Enhanced icon wrapper with glow effect */
.iconwrap button {{
  border: 2px solid {C['border']}; 
  background: {C['card_bg']};
  width: 52px; 
  height: 52px; 
  border-radius: 999px;
  box-shadow: 0 8px 28px rgba(0,0,0,.18); 
  backdrop-filter: blur(15px);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}}

.iconwrap button::before {{
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.6s;
}}

.iconwrap button:hover::before {{
  left: 100%;
}}

.iconwrap button:hover {{ 
  transform: scale(1.15) rotate(5deg);
  box-shadow: 0 15px 35px rgba(0,0,0,.3), 0 0 25px {C['accent']}50;
  border-color: {C['accent']};
  background: linear-gradient(180deg, {C['card_bg']}, rgba(255,255,255,0.1));
}}

.iconwrap button p {{ margin:0; font-size:22px; }}

/* Enhanced cards with better shadows, animations, and shimmer */
.card {{
  background: {C['card_bg']}; 
  border: 1px solid {C['border']};
  border-radius: 24px; 
  padding: 28px 32px; 
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 15px 50px rgba(0,0,0,.15); 
  backdrop-filter: blur(20px);
  position: relative;
  overflow: hidden;
  animation: slideIn 0.6s ease-out;
}}

.card::before {{
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
  transition: left 0.8s;
}}

.card:hover::before {{
  left: 100%;
}}

.card:hover {{ 
  transform: translateY(-8px) scale(1.03); 
  box-shadow: 0 25px 60px rgba(0,0,0,.25), 0 0 30px {C['accent']}30;
  border-color: {C['accent']}60;
  background: linear-gradient(180deg, {C['card_bg']}, rgba(255,255,255,0.05));
}}

.card h4 {{ 
  margin: 0; 
  color: {C['muted']}; 
  letter-spacing: .4px;
  font-size: 15px;
  text-transform: uppercase;
  font-weight: 700;
  margin-bottom: 8px;
}}

.card .big {{ 
  font-size: 48px; 
  font-weight: 900; 
  color: {C['text']}; 
  margin: 12px 0;
  background: linear-gradient(45deg, {C['accent']}, {C['accent2']}, {C['accent']});
  background-size: 200% 200%;
  -webkit-background-clip: text; 
  -webkit-text-fill-color: transparent;
}}

.card .trend {{
  font-size: 15px;
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  padding: 8px 12px;
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.1);
}}

/* Enhanced section headers with animations */
.section-header {{
  font-size: 32px;
  font-weight: 800;
  color: {C['text']};
  margin: 3rem 0 1.5rem 0;
  padding: 20px 28px;
  background: {C['card_bg']};
  border-radius: 20px;
  border: 1px solid {C['border']};
  backdrop-filter: blur(20px);
  text-align: center;
  position: relative;
  animation: slideIn 0.8s ease-out;
  box-shadow: 0 10px 40px rgba(0,0,0,.1);
}}

.section-header::before {{
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 5px;
  background: linear-gradient(180deg, {C['accent']}, {C['accent2']}, {C['accent']});
  border-radius: 0 3px 3px 0;
}}

.section-header::after {{
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 5px;
  background: linear-gradient(180deg, {C['accent2']}, {C['accent']}, {C['accent2']});
  border-radius: 3px 0 0 3px;
}}

/* Enhanced dividers */
hr {{ 
  border: 0; 
  height: 3px; 
  background: linear-gradient(90deg, transparent, {C['grid']}, {C['accent']}, {C['grid']}, transparent); 
  margin: 3rem 0;
  border-radius: 2px;
}}

/* Success/Error states with enhanced styling */
.success {{ 
  color: {C['success']}; 
  text-shadow: 0 0 10px {C['success']}40;
}}
.warning {{ 
  color: {C['warning']}; 
  text-shadow: 0 0 10px {C['warning']}40;
}}
.danger {{ 
  color: {C['danger']}; 
  text-shadow: 0 0 10px {C['danger']}40;
}}

/* Enhanced data table */
.dataframe {{
  border-radius: 20px;
  overflow: hidden;
  border: 2px solid {C['border']};
  box-shadow: 0 10px 30px rgba(0,0,0,.1);
}}

/* Floating action button with enhanced effects */
.fab {{
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: linear-gradient(45deg, {C['accent']}, {C['accent2']});
  color: white;
  border: none;
  box-shadow: 0 10px 30px rgba(0,0,0,.3), 0 0 20px {C['accent']}40;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  z-index: 1000;
  font-size: 16px;
  font-weight: 600;
}}

.fab:hover {{
  transform: scale(1.2) rotate(10deg);
  box-shadow: 0 15px 40px rgba(0,0,0,.4), 0 0 35px {C['accent']}70;
  background: linear-gradient(45deg, {C['accent2']}, {C['accent']});
}}

/* Enhanced metric styling */
.metric-container {{
  background: {C['card_bg']};
  border-radius: 16px;
  padding: 16px;
  border: 1px solid {C['border']};
  backdrop-filter: blur(15px);
  transition: all 0.3s ease;
  animation: slideIn 0.6s ease-out;
}}

.metric-container:hover {{
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0,0,0,.15);
}}

/* Enhanced chart containers */
.chart-container {{
  background: {C['card_bg']};
  border-radius: 20px;
  padding: 20px;
  border: 1px solid {C['border']};
  backdrop-filter: blur(15px);
  box-shadow: 0 10px 30px rgba(0,0,0,.1);
  animation: slideIn 0.8s ease-out;
}}

/* Loading animation */
.loading {{
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 3px solid {C['border']};
  border-radius: 50%;
  border-top-color: {C['accent']};
  animation: spin 1s ease-in-out infinite;
}}

@keyframes spin {{
  to {{ transform: rotate(360deg); }}
}}

/* Enhanced button styling */
.stButton > button {{
  border-radius: 12px !important;
  border: 2px solid {C['border']} !important;
  background: {C['card_bg']} !important;
  color: {C['text']} !important;
  backdrop-filter: blur(15px) !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 5px 15px rgba(0,0,0,.1) !important;
}}

.stButton > button:hover {{
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(0,0,0,.2) !important;
  border-color: {C['accent']} !important;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- Enhanced Header ----------------
st.markdown('<div class="title">Banking Analytics Workbench</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Advanced Analytics & Machine Learning for Modern Banking</div>', unsafe_allow_html=True)

# Theme toggle with enhanced positioning
col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
with col2:
    st.markdown('<div class="iconwrap">', unsafe_allow_html=True)
    icon = "☀️" if st.session_state["theme_mode"] == "Dark" else "🌙"
    if st.button(icon, key="toggle_theme", help="Toggle theme", type="secondary"):
        st.session_state["theme_mode"] = "Light" if st.session_state["theme_mode"] == "Dark" else "Dark"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Data Connection ----------------
@st.cache_resource(ttl=300)
def get_data():
    try:
        con = duckdb.connect("data/warehouse/baw.duckdb")
        con.execute("SET schema 'main_marts'")
        return con
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

con = get_data()

if con is None:
    st.error("Unable to connect to database. Please ensure the data pipeline has been run.")
    st.stop()

# ---------------- Enhanced KPIs with Trends ----------------
st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)

# Get KPI data
try:
    n_customers = con.execute("select count(*) from dim_customer").fetchone()[0]
    tx_7d = con.execute("""
      select coalesce(sum(amount),0)
      from fact_transactions
      where ts::date >= current_date - INTERVAL 7 DAY
    """).fetchone()[0]
    
    # Get previous period for trend calculation
    tx_14d = con.execute("""
      select coalesce(sum(amount),0)
      from fact_transactions
      where ts::date >= current_date - INTERVAL 14 DAY AND ts::date < current_date - INTERVAL 7 DAY
    """).fetchone()[0]
    
    tx_trend = ((tx_7d - tx_14d) / tx_14d * 100) if tx_14d > 0 else 0
    
    # Customer growth - using a different approach since created_date might not exist
    try:
        customers_30d = con.execute("""
          select count(*) from dim_customer 
          where created_date >= current_date - INTERVAL 30 DAY
        """).fetchone()[0]
        customer_trend = (customers_30d / n_customers * 100) if n_customers > 0 else 0
    except:
        # Fallback if created_date doesn't exist
        customer_trend = 0.0
    
except Exception as e:
    st.error(f"Error fetching KPI data: {e}")
    n_customers, tx_7d, tx_trend, customer_trend = 0, 0, 0, 0

# Fraud and churn data
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

# Enhanced KPI cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    trend_icon = "📈" if customer_trend > 0 else "📉"
    trend_color = "success" if customer_trend > 0 else "danger"
    st.markdown(f'''
        <div class="card">
            <h4>Total Customers</h4>
            <div class="big">{n_customers:,}</div>
            <div class="trend {trend_color}">
                {trend_icon} {customer_trend:.1f}% (30d)
            </div>
        </div>
    ''', unsafe_allow_html=True)

with col2:
    trend_icon = "📈" if tx_trend > 0 else "📉"
    trend_color = "success" if tx_trend > 0 else "danger"
    st.markdown(f'''
        <div class="card">
            <h4>Transaction Volume (7d)</h4>
            <div class="big">${tx_7d:,.0f}</div>
            <div class="trend {trend_color}">
                {trend_icon} {tx_trend:.1f}% vs prev week
            </div>
        </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
        <div class="card">
            <h4>High-Risk Alerts</h4>
            <div class="big">{alerts:,}</div>
            <div class="trend warning">
                Fraud detection active
            </div>
        </div>
    ''', unsafe_allow_html=True)

with col4:
    risk_level = "Low" if churn_risk < 20 else "Medium" if churn_risk < 40 else "High"
    risk_emoji = "🟢" if churn_risk < 20 else "🟡" if churn_risk < 40 else "🔴"
    st.markdown(f'''
        <div class="card">
            <h4>Churn Risk</h4>
            <div class="big">{churn_risk:.1f}%</div>
            <div class="trend warning">
                {risk_emoji} {risk_level} Risk Level
            </div>
        </div>
    ''', unsafe_allow_html=True)

# ---------------- Enhanced Transaction Analytics ----------------
st.markdown('<div class="section-header">Transaction Analytics</div>', unsafe_allow_html=True)

# Time window control with better styling
col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
with col2:
    window = st.selectbox("Time Window", ["30d", "60d", "90d"], index=0, label_visibility="collapsed")
win_days = int(window[:-1])

# Enhanced transaction volume chart
try:
    daily = con.execute(f"""
      select ts::date as d, sum(amount) as amt, count(*) as tx_count
      from fact_transactions
      where ts::date >= current_date - INTERVAL {win_days} DAY
      group by 1 order by 1
    """).fetch_df()
    
    # Create subplot with volume and count
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Transaction Volume", "Transaction Count"),
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )
    
    # Volume line
    fig.add_trace(
        go.Scatter(
            x=daily["d"], y=daily["amt"],
            mode="lines+markers",
            name="Volume",
            line=dict(color=C["accent"], width=4),
            marker=dict(size=8, color=C["accent"]),
            fill="tonexty",
            fillcolor=C['accent']
        ),
        row=1, col=1
    )
    
    # Count bars
    fig.add_trace(
        go.Bar(
            x=daily["d"], y=daily["tx_count"],
            name="Count",
            marker_color=C["accent2"],
            opacity=0.8
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        template=C["plot_template"],
        font=dict(color=C["text"]),
        height=600,
        showlegend=False,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified"
    )
    
    fig.update_xaxes(gridcolor=C["grid"], tickfont=dict(color=C["text"]), row=1, col=1)
    fig.update_yaxes(gridcolor=C["grid"], tickfont=dict(color=C["text"]), row=1, col=1)
    fig.update_xaxes(gridcolor=C["grid"], tickfont=dict(color=C["text"]), row=2, col=1)
    fig.update_yaxes(gridcolor=C["grid"], tickfont=dict(color=C["text"]), row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
except Exception as e:
    st.error(f"Error loading transaction data: {e}")

# ---------------- Enhanced ATM Forecast Visualization ----------------
st.markdown('<div class="section-header">ATM Cash Demand Forecast</div>', unsafe_allow_html=True)

try:
    atm_fc = pd.read_parquet("data/outputs/atm_forecast_7d.parquet").copy()
    atm_fc["date"] = pd.to_datetime(atm_fc["date"])
    
    # Create enhanced 3D surface
    grid = atm_fc.pivot_table(index="branch_id", columns="date", values="cash_forecast", aggfunc="mean").sort_index()
    z = grid.values
    x = [d.strftime("%b %d") for d in grid.columns]
    y = grid.index.astype(int)
    
    # Enhanced 3D surface with better colors
    surface = go.Figure(data=[go.Surface(
        z=z, x=x, y=y, 
        colorscale="Viridis", 
        opacity=0.9,
        contours=dict(
            z=dict(show=True, usecolormap=True, highlightcolor=C["accent"], project_z=True)
        )
    )])
    
    surface.update_layout(
        template=C["plot_template"],
        font=dict(color=C["text"]),
        scene=dict(
            xaxis_title="Date",
            yaxis_title="Branch ID", 
            zaxis_title="Cash Forecast ($)",
            xaxis=dict(gridcolor=C["grid"], tickfont=dict(color=C["text"])),
            yaxis=dict(gridcolor=C["grid"], tickfont=dict(color=C["text"])),
            zaxis=dict(gridcolor=C["grid"], tickfont=dict(color=C["text"]))
        ),
        height=600,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        title=dict(
            text="7-Day Cash Demand Forecast by Branch",
            font=dict(size=20, color=C["text"])
        )
    )
    
    st.plotly_chart(surface, use_container_width=True)
    
    # Add summary statistics with enhanced styling
    col1, col2, col3 = st.columns(3)
    with col1:
        total_forecast = atm_fc["cash_forecast"].sum()
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="margin: 0; color: {C['muted']}; font-size: 14px; text-transform: uppercase;">Total Forecast</h4>
            <div style="font-size: 28px; font-weight: 800; color: {C['accent']}; margin: 8px 0;">${total_forecast:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        avg_forecast = atm_fc["cash_forecast"].mean()
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="margin: 0; color: {C['muted']}; font-size: 14px; text-transform: uppercase;">Average Forecast</h4>
            <div style="font-size: 28px; font-weight: 800; color: {C['accent2']}; margin: 8px 0;">${avg_forecast:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        max_forecast = atm_fc["cash_forecast"].max()
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="margin: 0; color: {C['muted']}; font-size: 14px; text-transform: uppercase;">Peak Demand</h4>
            <div style="font-size: 28px; font-weight: 800; color: {C['success']}; margin: 8px 0;">${max_forecast:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        
except Exception as e:
    st.info("Run `python scripts/atm_forecast.py` to generate forecasts.")
    st.caption(f"Debug info: {e}")

# ---------------- Enhanced Fraud Analytics ----------------
st.markdown('<div class="section-header">Fraud Detection & Risk Analysis</div>', unsafe_allow_html=True)

try:
    tx = con.execute("select tx_id, customer_id, amount, ts from fact_transactions").fetch_df()
    fraud = pd.read_parquet("data/outputs/fraud_scores.parquet")
    
    # Merge and get top fraud cases
    top = (tx.merge(fraud, on=["customer_id","amount"], how="inner")
             .sort_values("fraud_score", ascending=False)
             .head(50)[["tx_id","customer_id","amount","ts","fraud_score"]])
    
    # Enhanced risk tiers with better categorization
    q95 = top["fraud_score"].quantile(0.95)
    q80 = top["fraud_score"].quantile(0.80)
    
    def tier(s):
        if s >= q95: return "Critical"
        if s >= q80: return "High"
        return "Medium"
    
    top["risk_tier"] = top["fraud_score"].apply(tier)
    top["ts"] = pd.to_datetime(top["ts"])
    
    # Risk distribution chart
    risk_counts = top["risk_tier"].value_counts()
    fig_pie = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        color_discrete_map={
            "Critical": C["danger"],
            "High": C["warning"],
            "Medium": C["success"]
        },
        title="Risk Distribution"
    )
    
    fig_pie.update_layout(
        template=C["plot_template"],
        font=dict(color=C["text"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    col1, col2 = st.columns([0.6, 0.4])
    
    with col1:
        st.subheader("Top Fraud Alerts")
        max_score = float(top["fraud_score"].max() or 1.0)
        st.dataframe(
            top,
            hide_index=True,
            use_container_width=True,
            column_config={
                "tx_id": st.column_config.NumberColumn("Transaction ID"),
                "customer_id": st.column_config.NumberColumn("Customer ID"),
                "amount": st.column_config.NumberColumn("Amount", format="$%0.2f"),
                "ts": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm"),
                "fraud_score": st.column_config.ProgressColumn(
                    "Risk Score", min_value=0.0, max_value=max_score, format="%0.3f"
                ),
                "risk_tier": st.column_config.TextColumn("Risk Level"),
            }
        )
        
        # Download button
        csv = top.to_csv(index=False).encode()
        st.download_button(
            "Download Alerts (CSV)", 
            data=csv, 
            file_name="fraud_alerts.csv",
            mime="text/csv", 
            type="secondary"
        )
    
    with col2:
        st.subheader("Risk Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Summary metrics with enhanced styling
        st.markdown(f"""
        <div class="metric-container" style="margin-bottom: 16px;">
            <h4 style="margin: 0; color: {C['muted']}; font-size: 14px; text-transform: uppercase;">Critical Alerts</h4>
            <div style="font-size: 28px; font-weight: 800; color: {C['danger']}; margin: 8px 0;">{len(top[top['risk_tier'] == 'Critical'])}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-container" style="margin-bottom: 16px;">
            <h4 style="margin: 0; color: {C['muted']}; font-size: 14px; text-transform: uppercase;">High Risk</h4>
            <div style="font-size: 28px; font-weight: 800; color: {C['warning']}; margin: 8px 0;">{len(top[top['risk_tier'] == 'High'])}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="margin: 0; color: {C['muted']}; font-size: 14px; text-transform: uppercase;">Total Alerts</h4>
            <div style="font-size: 28px; font-weight: 800; color: {C['text']}; margin: 8px 0;">{len(top)}</div>
        </div>
        """, unsafe_allow_html=True)
        
except Exception as e:
    st.info("Run `python scripts/fraud_isoforest.py` to generate fraud scores.")
    st.caption(f"Debug info: {e}")

# ---------------- Customer Insights Section ----------------
st.markdown('<div class="section-header">Customer Analytics & Insights</div>', unsafe_allow_html=True)

try:
    # Customer demographics - check what columns exist
    try:
        # First, let's see what columns are available
        columns = con.execute("DESCRIBE dim_customer").fetch_df()
        st.write("Available columns:", columns)
        
        # Try to get customer data with available columns
        customers = con.execute("""
            select 
                age,
                count(*) as customer_count
            from dim_customer 
            group by age 
            order by age asc
        """).fetch_df()
    except Exception as e:
        st.info(f"Customer demographics not available: {e}")
        customers = pd.DataFrame()
    
    # Create customer insights visualization only if we have data
    if not customers.empty and len(customers) > 0:
        # Create age distribution chart
        fig_age = px.bar(
            customers, 
            x="age", 
            y="customer_count",
            title="Customer Distribution by Age",
            labels={"age": "Age", "customer_count": "Number of Customers"},
            color_discrete_sequence=[C["accent"]]
        )
        
        fig_age.update_layout(
            template=C["plot_template"],
            font=dict(color=C["text"]),
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor=C["grid"], tickfont=dict(color=C["text"])),
            yaxis=dict(gridcolor=C["grid"], tickfont=dict(color=C["text"]))
        )
        
        st.plotly_chart(fig_age, use_container_width=True)
        
        # Add some summary statistics with enhanced styling
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <h4 style="margin: 0; color: {C['muted']}; font-size: 14px; text-transform: uppercase;">Total Customers</h4>
                <div style="font-size: 28px; font-weight: 800; color: {C['accent']}; margin: 8px 0;">{customers['customer_count'].sum():,}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <h4 style="margin: 0; color: {C['muted']}; font-size: 14px; text-transform: uppercase;">Average Age</h4>
                <div style="font-size: 28px; font-weight: 800; color: {C['accent2']}; margin: 8px 0;">{customers['age'].mean():.1f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <h4 style="margin: 0; color: {C['muted']}; font-size: 14px; text-transform: uppercase;">Age Range</h4>
                <div style="font-size: 28px; font-weight: 800; color: {C['success']}; margin: 8px 0;">{customers['age'].min()} - {customers['age'].max()}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Customer demographics data not available")
    
except Exception as e:
    st.info("Customer data not available")

# ---------------- Footer with Status ----------------
st.markdown("---")
col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
with col2:
    st.markdown(f"""
    <div style="text-align: center; color: {C['muted']}; font-size: 14px;">
        BAW Dashboard v2.0 | Powered by Streamlit & Plotly
    </div>
    """, unsafe_allow_html=True)

# Floating action button for quick actions
st.markdown("""
<div class="fab" onclick="alert('🚀 Quick actions coming soon!\\n\\n• Export Data\\n• Generate Reports\\n• System Status\\n• Help & Support')">
    ⚡
</div>
""", unsafe_allow_html=True)
