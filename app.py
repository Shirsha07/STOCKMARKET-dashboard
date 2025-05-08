import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import ta

# App Title
st.title("Stock Market Visualizer with Enhanced Analytics")
st.sidebar.title("Options")

# Helper Functions
def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    return stock.history(start=start_date, end=end_date)

def plot_candlestick(data):
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
    fig = px.bar(data, x=data.index, y='Volume', title="Trading Volume", template="plotly_dark")
    st.plotly_chart(fig)

def plot_daily_returns(data):
    data['Daily Return'] = data['Close'].pct_change() * 100
    fig = px.line(data, x=data.index, y='Daily Return', title="Daily Returns (%)", template="plotly_dark")
    st.plotly_chart(fig)

def plot_cumulative_returns(data):
    data['Cumulative Return'] = (1 + data['Close'].pct_change()).cumprod() - 1
    fig = px.line(data, x=data.index, y='Cumulative Return', title="Cumulative Returns", template="plotly_dark")
    st.plotly_chart(fig)

def plot_moving_averages(data, windows):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name="Close Price"))
    for window in windows:
        data[f"MA{window}"] = data['Close'].rolling(window=window).mean()
        fig.add_trace(go.Scatter(x=data.index, y=data[f"MA{window}"], mode='lines', name=f"MA {window}"))
    fig.update_layout(title="Moving Averages", xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
    st.plotly_chart(fig)

def plot_correlation_matrix(data):
    corr = data.corr()
    fig = px.imshow(corr, title="Correlation Matrix", template="plotly_dark", text_auto=True, color_continuous_scale='RdBu_r')
    st.plotly_chart(fig)

# Fetch Nifty 200 list (hardcoded sample for demo – replace with full list or API if needed)
nifty_200 = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "WIPRO.NS", "LT.NS", "HCLTECH.NS"
]

# Sidebar Inputs
st.sidebar.header("Stock Selection")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL)", value="RELIANCE.NS")
start_date = st.sidebar.date_input("Start Date", value=date(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", value=date.today())

data = fetch_stock_data(ticker, start_date, end_date)

# Stock Visualizations
if not data.empty:
    st.subheader(f"Stock Data for {ticker}")
    st.write(data.tail())

    st.subheader("Candlestick Chart")
    plot_candlestick(data)

    st.subheader("Volume Chart")
    plot_volume(data)

    st.subheader("Daily Returns")
    plot_daily_returns(data)

    st.subheader("Cumulative Returns")
    plot_cumulative_returns(data)

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

# Top Gainers & Losers in Nifty 200
st.subheader("📈 Top Gainers & 📉 Losers (Nifty 200)")
gain_data = []
for t in nifty_200:
    try:
        df = fetch_stock_data(t, date.today().replace(year=date.today().year - 1), date.today())
        if len(df) >= 2:
            change = ((df['Close'][-1] - df['Close'][-2]) / df['Close'][-2]) * 100
            gain_data.append((t, change))
    except:
        pass

sorted_gainers = sorted(gain_data, key=lambda x: x[1], reverse=True)
st.write("### 🔼 Top 5 Gainers")
st.table(sorted_gainers[:5])

st.write("### 🔽 Top 5 Losers")
st.table(sorted_gainers[-5:])

# Upward Trend Stocks based on TA
st.subheader("📊 Upward Trend Stocks in Nifty 200")
upward_trend_stocks = []

for t in nifty_200:
    try:
        df = fetch_stock_data(t, start_date, end_date)
        if df.empty or len(df) < 50:
            continue

        # TA indicators
        df['EMA'] = ta.trend.ema_indicator(df['Close'], window=20).fillna(0)
        macd = ta.trend.macd(df['Close']).fillna(0)
        rsi = ta.momentum.RSIIndicator(df['Close']).rsi().fillna(0)
        boll = ta.volatility.BollingerBands(df['Close'])

        macd_val = macd.iloc[-1]
        rsi_val = rsi.iloc[-1]
        close = df['Close'].iloc[-1]
        upper_band = boll.bollinger_hband().iloc[-1]
        ema = df['EMA'].iloc[-1]

        if macd_val > 0 and rsi_val > 50 and close >= upper_band and close > ema:
            upward_trend_stocks.append(t)
    except:
        continue

selected_upward = st.selectbox("Select upward trending stock", options=upward_trend_stocks if upward_trend_stocks else ["None"])

# 📩 Contact Me
st.sidebar.markdown("---")
st.sidebar.markdown("📬 **Contact Me**")
if st.sidebar.button("Get in Touch"):
    st.sidebar.markdown("📧 Email: yourname@example.com")
    st.sidebar.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/yourprofile)")
