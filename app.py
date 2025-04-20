import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

# App Title
st.title("Interactive Stock Market Dashboard")
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
st.sidebar.subheader("📊 Portfolio Analysis")
uploaded_file = st.sidebar.file_uploader("Upload Portfolio (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            portfolio = pd.read_csv(uploaded_file)
        else:
            portfolio = pd.read_excel(uploaded_file)

        # Check for required column
        if 'Symbol' not in portfolio.columns:
            st.sidebar.error("❌ Uploaded file must contain a 'Symbol' column with stock symbols like INFY.NS or TCS.NS")
            st.stop()

        tickers = portfolio['Symbol'].dropna().unique().tolist()

        st.subheader("📁 Portfolio Overview")
        st.write(portfolio)

        st.subheader("📈 Portfolio Stock Charts")
        for symbol in tickers:
            st.markdown(f"### {symbol}")
            data = yf.download(symbol, period="6mo", interval="1d")
            fig = go.Figure(data=[go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close']
            )])
            fig.update_layout(title=f"{symbol} - 6 Month Candlestick Chart", xaxis_title="Date", yaxis_title="Price")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.sidebar.error(f"⚠️ Error processing file: {e}")

