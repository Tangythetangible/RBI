import streamlit as st
import pandas as pd
from datetime import timedelta

st.set_page_config(page_title="Research Hub – MVP", layout="wide")
st.title("Research Hub – MVP")

st.markdown("""
**Internal Research Accelerator**
Upload your raw data exports below to generate instant insight.
""")

st.divider()

# ==========================================
# 1. UPLOAD SECTION
# ==========================================
st.sidebar.header("📂 Data Import")
prices_file = st.sidebar.file_uploader("Prices (CSV)", type="csv")
consensus_file = st.sidebar.file_uploader("Consensus (CSV)", type="csv")
earnings_file = st.sidebar.file_uploader("Earnings (CSV)", type="csv")

# Helper: Data Validation
def load_and_validate(file, required_cols, date_cols, name):
    if file is None:
        return None
    try:
        df = pd.read_csv(file)
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"❌ {name} file is missing columns: {missing}")
            st.stop()
        for d in date_cols:
            df[d] = pd.to_datetime(df[d], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading {name}: {e}")
        st.stop()

# Load Data
prices = load_and_validate(prices_file, ["ticker", "date", "price"], ["date"], "Prices")
cons = load_and_validate(consensus_file, ["ticker", "asof_date", "fiscal_period", "metric", "value"], ["asof_date"], "Consensus")
earn = load_and_validate(earnings_file, ["ticker", "fiscal_period", "reported_date", "actual", "estimate", "metric"], ["reported_date"], "Earnings")

if not any([prices is not None, cons is not None, earn is not None]):
    st.info("👈 Upload at least one CSV file in the sidebar to start.")
    st.stop()

# ==========================================
# 2. TICKER SELECTION
# ==========================================
tickers = set()
for df in [prices, cons, earn]:
    if df is not None:
        tickers |= set(df["ticker"].dropna().unique())

if not tickers:
    st.warning("No tickers found in uploaded data.")
    st.stop()

selected_ticker = st.selectbox("Select Company:", sorted(tickers))

# Filter data for selected ticker
p_data = prices[prices["ticker"] == selected_ticker].sort_values("date") if prices is not None else pd.DataFrame()
c_data = cons[cons["ticker"] == selected_ticker].sort_values("asof_date") if cons is not None else pd.DataFrame()
e_data = earn[earn["ticker"] == selected_ticker].sort_values("reported_date") if earn is not None else pd.DataFrame()

st.divider()

# ==========================================
# 3. DASHBOARD LOGIC
# ==========================================
col1, col2, col3 = st.columns(3)

# --- Metric 1: Latest Price ---
with col1:
    st.subheader("Market Data")
    if not p_data.empty:
        latest_px = p_data.iloc[-1]['price']
        latest_date = p_data.iloc[-1]['date'].strftime('%Y-%m-%d')
        st.metric("Last Price", f"{latest_px:,.2f}", delta=None, help=f"As of {latest_date}")
    else:
        st.write("No price data.")

# --- Metric 2: Consensus Estimates ---
with col2:
    st.subheader("Forward Estimates")
    if not c_data.empty:
        # Get unique periods and metrics
        periods = c_data["fiscal_period"].unique()
        target_period = st.selectbox("Fiscal Period", periods, index=0)
        
        # Filter for EPS
        eps_data = c_data[(c_data["fiscal_period"] == target_period) & (c_data["metric"] == "EPS")]
        
        if not eps_data.empty:
            current_eps = eps_data.iloc[-1]['value']
            st.metric(f"Consensus EPS ({target_period})", f"{current_eps:.2f}")
        else:
            st.write("No EPS data for this period.")
    else:
        st.write("No consensus data.")

# --- Metric 3: Revision Tracker (The "Alpha" Tool) ---
with col3:
    st.subheader("⚠️ Revision Momentum")
    # This logic checks if analysts are upgrading/downgrading vs 30 days ago
    if not c_data.empty and 'eps_data' in locals() and not eps_data.empty:
        latest_date = eps_data['asof_date'].max()
        date_30d_ago = latest_date - timedelta(days=30)
        
        # Find estimate closest to 30 days ago
        past_ests = eps_data[eps_data['asof_date'] <= date_30d_ago]
        
        if not past_ests.empty:
            past_eps = past_ests.iloc[-1]['value']
            current_eps = eps_data.iloc[-1]['value']
            diff = (current_eps - past_eps) / abs(past_eps)
            
            # Color code the output
            if diff > 0.01:
                st.success(f"📈 Upgraded +{diff:.1%} (30d)")
            elif diff < -0.01:
                st.error(f"📉 Downgraded {diff:.1%} (30d)")
            else:
                st.warning(f"➡ Flat ({diff:.1%})")
        else:
            st.write("Not enough history for 30d comparison.")
    else:
        st.write("Need consensus data to calc revisions.")

# ==========================================
# 4. CHARTS & VISUALS
# ==========================================
st.divider()

if not c_data.empty and 'eps_data' in locals() and not eps_data.empty:
    st.subheader("Estimate Revision History")
    st.markdown("Track how the consensus has changed over time. Look for **inflection points**.")
    st.line_chart(eps_data.set_index("asof_date")["value"])

if not e_data.empty:
    st.subheader("Earnings Surprise History")
    # Simple table for beat/miss
    disp_cols = ["fiscal_period", "reported_date", "actual", "estimate", "metric"]
    st.dataframe(e_data[disp_cols].sort_values("reported_date", ascending=False), use_container_width=True)