import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from datetime import datetime

st.set_page_config(page_title="Interactive Stock Market Dashboard", layout="wide")
st.title("📈 Interactive Stock Market Dashboard")

# --- Timeframe selection ---
timeframe_map = {
    "Today (Intraday)": ("1d", "5m"),
    "1 Day": ("5d", "1d"),
    "1 Week": ("1mo", "1h"),
    "1 Month": ("3mo", "1d"),
    "3 Months": ("6mo", "1d"),
    "6 Months": ("1y", "1d"),
    "1 Year": ("1y", "1d"),
    "5 Years": ("5y", "1d")
}
timeframe = st.selectbox("Select Timeframe", list(timeframe_map.keys()))
period, interval = timeframe_map[timeframe]

# --- Stock selection ---
stocks = st.multiselect("Enter Stock Symbols (e.g., INFY.NS, TCS.NS)", ["RELIANCE.NS", "INFY.NS", "TCS.NS", "HDFCBANK.NS"])

# --- Load and process stock data ---
def get_stock_data(symbol):
    df = yf.download(symbol, period=period, interval=interval)
    if df.empty:
        return None
    df["EMA20"] = EMAIndicator(df["Close"], window=20).ema_indicator()
    df["RSI"] = RSIIndicator(df["Close"]).rsi()
    macd = MACD(close=df["Close"])
    df["MACD"] = macd.macd()
    bb = BollingerBands(close=df["Close"])
    df["BB_High"] = bb.bollinger_hband()
    df["BB_Low"] = bb.bollinger_lband()
    df.dropna(inplace=True)
    return df

# --- Identify upward trend stocks ---
upward_stocks = []
stock_details = []

for symbol in stocks:
    df = get_stock_data(symbol)
    if df is not None and not df.empty:
        last = df.iloc[-1]
        if (
            last["MACD"] > 0
            and last["RSI"] > 50
            and last["Close"] >= last["BB_High"] * 0.98
            and last["EMA20"] < last["Close"]
        ):
            upward_stocks.append(symbol)

            ticker = yf.Ticker(symbol)
            info = ticker.info
            current_price = last["Close"]
            previous_close = info.get("previousClose", np.nan)
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close else 0
            stock_details.append({
                "Symbol": symbol,
                "Current Price": f"{current_price:.2f}",
                "Yesterday Close": f"{previous_close:.2f}",
                "Change": f"{change:.2f}",
                "Change %": f"{change_percent:.2f}%",
                "52W High": info.get("fiftyTwoWeekHigh", "-"),
                "52W Low": info.get("fiftyTwoWeekLow", "-")
            })

# --- Display upward trend stocks ---
st.subheader("📊 Stocks in Upward Trend")
if stock_details:
    st.dataframe(pd.DataFrame(stock_details))
else:
    st.info("No stocks meeting the upward trend criteria.")

# --- Candlestick Chart ---
st.subheader("📈 Candlestick Chart with Indicators")
selected_stock = st.selectbox("Select a stock to visualize", stocks)
if selected_stock:
    df = get_stock_data(selected_stock)
    if df is not None:
        fig = go.Figure(data=[
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Candlestick"
            ),
            go.Scatter(x=df.index, y=df["EMA20"], mode="lines", name="EMA20", line=dict(color="orange")),
            go.Scatter(x=df.index, y=df["BB_High"], mode="lines", name="BB Upper", line=dict(color="green")),
            go.Scatter(x=df.index, y=df["BB_Low"], mode="lines", name="BB Lower", line=dict(color="red"))
        ])
        fig.update_layout(xaxis_rangeslider_visible=False, height=600)
        st.plotly_chart(fig, use_container_width=True)

# --- Upload Looker/Sheet Reports ---
st.subheader("📁 Upload Your Dashboard Reports")
uploaded_file = st.file_uploader("Upload CSV/XLSX report or paste Google Sheet/Looker URL below")
sheet_url = st.text_input("Or paste public Google Sheet/Looker dashboard URL")

report_df = None

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        report_df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        report_df = pd.read_excel(uploaded_file)

elif sheet_url:
    try:
        if "docs.google.com" in sheet_url:
            sheet_url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
        report_df = pd.read_csv(sheet_url)
    except Exception as e:
        st.error(f"Failed to load data from URL: {e}")

if report_df is not None:
    st.success("Dashboard report loaded successfully!")
    st.dataframe(report_df.head())

