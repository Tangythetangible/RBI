import streamlit as st
import pandas as pd

st.set_page_config(page_title="Research Hub – MVP", layout="wide")
st.title("Research Hub – MVP")

st.markdown("""
Internal research accelerator.
Upload Bloomberg / LSEG exports and move from **raw data → insight**.
""")

st.divider()

# ---------- Upload ----------
st.header("📤 Upload data")

prices_file = st.file_uploader("Prices (CSV)", type="csv")
consensus_file = st.file_uploader("Consensus / estimates (CSV)", type="csv")
earnings_file = st.file_uploader("Earnings actuals vs estimates (CSV)", type="csv")

# ---------- Helpers ----------
def validate(df, required_cols, name):
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"{name} is missing columns: {missing}")
        st.stop()

# ---------- Load & validate ----------
prices = cons = earn = None

if prices_file:
    prices = pd.read_csv(prices_file)
    validate(prices, ["ticker", "date", "price"], "Prices")
    prices["date"] = pd.to_datetime(prices["date"], errors="coerce")

if consensus_file:
    cons = pd.read_csv(consensus_file)
    validate(cons, ["ticker", "asof_date", "fiscal_period", "metric", "value"], "Consensus")
    cons["asof_date"] = pd.to_datetime(cons["asof_date"], errors="coerce")

if earnings_file:
    earn = pd.read_csv(earnings_file)
    validate(earn, ["ticker", "fiscal_period", "reported_date", "actual", "estimate", "metric"], "Earnings")
    earn["reported_date"] = pd.to_datetime(earn["reported_date"], errors="coerce")

if not any([prices is not None, cons is not None, earn is not None]):
    st.info("Upload at least one file to begin.")
    st.stop()

st.success("Data loaded successfully.")
st.write("Hello world")  # <- visible marker

st.divider()

# ---------- Ticker universe ----------
tickers = set()
for df in [prices, cons, earn]:
    if df is not None:
        tickers |= set(df["ticker"].dropna().unique())

ticker = st.selectbox("Select company", sorted(tickers))

st.divider()

# ---------- Company snapshot ----------
st.header(f"📊 {ticker} — Snapshot")

if prices is not None:
    px = prices[prices["ticker"] == ticker].sort_values("date")
    if not px.empty:
        st.metric("Last price", f"{px.iloc[-1]['price']:,.2f}")
