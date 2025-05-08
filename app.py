import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

# App Title
st.title("Stock Market Visualizer with Enhanced Analytics")
st.sidebar.title("Options")

# Helper Functions
def fetch_stock_data(ticker, start_date, end_date):
    """Fetch stock data using yfinance."""
    stock = yf.Ticker(ticker)
    return stock.history(start=start_date, end=end_date)

def plot_candlestick(data):
    """Plot a candlestick chart."""
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Candlestick"
    ))
    fig.update_layout(title="Candlestick Chart", xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
    st.plotly_chart(fig)

def plot_volume(data):
    """Plot a volume chart."""
    fig = px.bar(data, x=data.index, y='Volume', title="Trading Volume", template="plotly_dark")
    st.plotly_chart(fig)

def plot_daily_returns(data):
    """Plot daily returns."""
    data['Daily Return'] = data['Close'].pct_change() * 100
    fig = px.line(data, x=data.index, y='Daily Return', title="Daily Returns (%)", template="plotly_dark")
    st.plotly_chart(fig)

def plot_cumulative_returns(data):
    """Plot cumulative returns."""
    data['Cumulative Return'] = (1 + data['Close'].pct_change()).cumprod() - 1
    fig = px.line(data, x=data.index, y='Cumulative Return', title="Cumulative Returns", template="plotly_dark")
    st.plotly_chart(fig)

def plot_moving_averages(data, windows):
    """Plot moving averages."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name="Close Price"))
    for window in windows:
        data[f"MA{window}"] = data['Close'].rolling(window=window).mean()
        fig.add_trace(go.Scatter(x=data.index, y=data[f"MA{window}"], mode='lines', name=f"MA {window}"))
    fig.update_layout(title="Moving Averages", xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
    st.plotly_chart(fig)

def plot_correlation_matrix(data):
    """Plot correlation matrix for stock portfolio."""
    corr = data.corr()
    fig = px.imshow(corr, title="Correlation Matrix", template="plotly_dark", text_auto=True, color_continuous_scale='RdBu_r')
    st.plotly_chart(fig)

# Inputs
st.sidebar.header("Stock Selection")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL)", value="AAPL")
start_date = st.sidebar.date_input("Start Date", value=date(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", value=date.today())

data = fetch_stock_data(ticker, start_date, end_date)

# Visualizations
if not data.empty:
    st.subheader(f"Stock Data for {ticker}")
    st.write(data.tail())

    # Candlestick Chart
    st.subheader("Candlestick Chart")
    plot_candlestick(data)

    # Volume Chart
    st.subheader("Volume Chart")
    plot_volume(data)

    # Daily Returns
    st.subheader("Daily Returns")
    plot_daily_returns(data)

    # Cumulative Returns
    st.subheader("Cumulative Returns")
    plot_cumulative_returns(data)

    # Moving Averages
    st.sidebar.header("Moving Averages")
    moving_averages = st.sidebar.multiselect("Select Moving Averages (days)", options=[10, 20, 50, 100, 200], default=[20, 50])
    if moving_averages:
        st.subheader("Moving Averages")
        plot_moving_averages(data, moving_averages)

# Portfolio Correlation
st.sidebar.header("Portfolio Analysis")
portfolio_file = st.sidebar.file_uploader("Upload Portfolio (CSV or Excel)")
if portfolio_file:
    portfolio = pd.read_csv(portfolio_file) if portfolio_file.name.endswith("csv") else pd.read_excel(portfolio_file)
    tickers = portfolio['Ticker'].tolist()
    st.subheader("Portfolio Data")
    st.write(portfolio)

    portfolio_data = {t: fetch_stock_data(t, start_date, end_date)['Close'] for t in tickers}
    portfolio_df = pd.DataFrame(portfolio_data)
    st.subheader("Correlation Matrix")
    plot_correlation_matrix(portfolio_df)

# ==========================
# 🔻 MARKET SUMMARY SECTION
# ==========================

st.markdown("---")
st.header("📊 Market Summary: Gainers, Losers & Trend")

# Define a list of sample tickers (replace with actual index tickers if desired)
market_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'INTC', 'CSCO']
price_changes = {}

for symbol in market_tickers:
    try:
        df = fetch_stock_data(symbol, start_date, end_date)
        if len(df) >= 2:
            change = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
            price_changes[symbol] = round(change, 2)
    except:
        continue

# Sort to get top gainers and losers
sorted_changes = dict(sorted(price_changes.items(), key=lambda item: item[1], reverse=True))
gainers = dict(list(sorted_changes.items())[:5])
losers = dict(list(sorted_changes.items())[-5:])

col1, col2 = st.columns(2)
with col1:
    st.subheader("🚀 Top Gainers")
    st.write(pd.DataFrame(gainers.items(), columns=["Ticker", "Change (%)"]))

with col2:
    st.subheader("📉 Top Losers")
    st.write(pd.DataFrame(losers.items(), columns=["Ticker", "Change (%)"]))

# ==========================
# 📈 TREND DETECTION SECTION
# ==========================
st.markdown("## 📈 Trend Detection for Selected Stock")

if not data.empty:
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['MA200'] = data['Close'].rolling(window=200).mean()

    try:
        if data['Close'].iloc[-1] > data['MA50'].iloc[-1] > data['MA200'].iloc[-1]:
            st.success(f"✅ Upward Trend Detected for **{ticker}**!")
        else:
            st.info(f"ℹ️ No clear upward trend detected for **{ticker}**.")
    except:
        st.warning("⚠️ Not enough data for trend detection.")
