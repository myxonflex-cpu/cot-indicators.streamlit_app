import streamlit as st
import pandas as pd
import plotly.express as px
from cot_reports import CotReports
import datetime as dt

st.set_page_config(page_title="COT Explorer", layout="wide")
st.title("Commitment of Traders — Explorer")

# Sidebar controls
st.sidebar.header("Controls")
report_type = st.sidebar.selectbox("Report Type", 
                                   ["legacy_futures_only", "legacy_combined", 
                                    "disaggregated_futures_only", "disaggregated_combined"])
symbol_input = st.sidebar.text_input("Market / Symbol (full name)", 
                                     value="EURO FX - CHICAGO MERCANTILE EXCHANGE")
start_date = st.sidebar.date_input("Start date", value=dt.date.today() - dt.timedelta(days=365*2))
end_date = st.sidebar.date_input("End date", value=dt.date.today())

# Load COT data
@st.cache_data(ttl=3600)
def load_cot(report, market):
    cr = CotReports()
    try:
        df = cr.get_report(report, market)
        if isinstance(df, dict):
            df = pd.DataFrame(list(df.values())[0])
        elif isinstance(df, list):
            df = pd.DataFrame(df)
        # Detect date column
        date_cols = [c for c in df.columns if "date" in c.lower()]
        if date_cols:
            df.rename(columns={date_cols[0]: "Date"}, inplace=True)
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date").reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"Error loading COT data: {e}")
        return pd.DataFrame()

if st.sidebar.button("Load Data"):
    df = load_cot(report_type, symbol_input)
else:
    df = pd.DataFrame()

if df.empty:
    st.warning("No data loaded. Enter a valid market name and click Load Data.")
    st.stop()

# Column detection (simplified)
long_col = next((c for c in df.columns if "long" in c.lower()), None)
short_col = next((c for c in df.columns if "short" in c.lower()), None)
oi_col = next((c for c in df.columns if "open" in c.lower()), None)

if not long_col or not short_col:
    st.error("Could not detect Long or Short columns. Edit column names manually if needed.")
    st.stop()

df["Long"] = pd.to_numeric(df[long_col], errors="coerce")
df["Short"] = pd.to_numeric(df[short_col], errors="coerce")
df["Net"] = df["Long"] - df["Short"]
if oi_col:
    df["OI"] = pd.to_numeric(df[oi_col], errors="coerce")
    df["Long_pct"] = df["Long"] / df["OI"] * 100
    df["Short_pct"] = df["Short"] / df["OI"] * 100
    df["Net_pct"] = df["Net"] / df["OI"] * 100

# Filter by date
df = df[(df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)]

# Tabs
tabs = st.tabs(["Charts", "Table & Export"])
with tabs[0]:
    st.subheader("Net Positions")
    fig = px.line(df, x="Date", y=["Long", "Short", "Net"], title=f"{symbol_input} COT Positions")
    st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.subheader("Data Table")
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, file_name=f"COT_{symbol_input}.csv")
