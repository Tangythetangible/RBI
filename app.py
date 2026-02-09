import streamlit as st
import pandas as pd

st.set_page_config(page_title="Research Hub – MVP", layout="wide")

st.title("Research Hub – MVP")

st.markdown("""
This tool is an **internal research accelerator**.

Upload Bloomberg / LSEG exports and get:
- expectation & revision signals  
- earnings surprise snapshots  
- a consistent company view
""")

st.divider()

# --- Upload section ---
st.header("📤 Upload data")

prices_file = st.file_uploader("Upload prices export (CSV)", type=["csv"])
consensus_file = st.file_uploader("Upload consensus / estimates (CSV)", type=["csv"])
earnings_file = st.file_uploader("Upload earnings actuals vs estimates (CSV)", type=["csv"])

st.divider()

if prices_file:
    prices = pd.read_csv(prices_file)
    st.subheader("Prices preview")
    st.dataframe(prices.head(), use_container_width=True)

if consensus_file:
    cons = pd.read_csv(consensus_file)
    st.subheader("Consensus preview")
    st.dataframe(cons.head(), use_container_width=True)

if earnings_file:
    earn = pd.read_csv(earnings_file)
    st.subheader("Earnings preview")
    st.dataframe(earn.head(), use_container_width=True)

if not any([prices_file, consensus_file, earnings_file]):
    st.info("Upload at least one file to begin.")
