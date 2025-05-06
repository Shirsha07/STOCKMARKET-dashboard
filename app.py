import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime, timedelta

# App Title
st.title("Interactive Stock Market Dashboard")
st.sidebar.title("Options")

# Helper Functions
def fetch_stock_data(ticker, start_date, end_date):
    """Fetch stock data using yfinance."""
    stock = yf.Ticker(ticker)
    return stock.history(start=start_date, end=end_date)
def get_top_gainers_losers():
    # List of stock symbols you want to track (replace with your list)
    symbols = ['ADANIENSOL.NS', 'ADANIENT.NS', 'ADANIPORTS.NS', 'ADANITRANS.NS', 'ALKEM.NS',
    'AMBUJACEM.NS', 'APLLTD.NS', 'APOLLOHOSP.NS', 'AUROPHARMA.NS', 'AXISBANK.NS',
    'BAJAJ-AUTO.NS', 'BAJAJFINSV.NS', 'BAJFINANCE.NS', 'BALKRISIND.NS', 'BANDHANBNK.NS',
    'BANKBARODA.NS', 'BATAINDIA.NS', 'BEL.NS', 'BHARATFORG.NS', 'BHARTIARTL.NS',
    'BIOCON.NS', 'BOSCHLTD.NS', 'BPCL.NS', 'BRITANNIA.NS', 'CANBK.NS',
    'CHOLAFIN.NS', 'CIPLA.NS', 'COALINDIA.NS', 'COLPAL.NS', 'CONCOR.NS',
    'CROMPTON.NS', 'DABUR.NS', 'DALBHARAT.NS', 'DIVISLAB.NS', 'DLF.NS',
    'DMART.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'GAIL.NS', 'GLAND.NS',
    'GODREJCP.NS', 'GODREJPROP.NS', 'GRASIM.NS', 'GUJGASLTD.NS', 'HAVELLS.NS',
    'HCLTECH.NS', 'HDFCAMC.NS', 'HDFCBANK.NS', 'HDFCLIFE.NS', 'HEROMOTOCO.NS',
    'HINDALCO.NS', 'HINDPETRO.NS', 'HINDUNILVR.NS', 'ICICIBANK.NS', 'ICICIGI.NS',
    'ICICIPRULI.NS', 'IDBI.NS', 'IDFCFIRSTB.NS', 'IGL.NS', 'INDIGO.NS',
    'INDUSINDBK.NS', 'INDUSTOWER.NS', 'INFY.NS', 'IOC.NS', 'IRCTC.NS', 'ITC.NS',
    'JINDALSTEL.NS', 'JSWSTEEL.NS', 'JUBLFOOD.NS', 'KANSAINER.NS', 'KOTAKBANK.NS',
    'L&TFH.NS', 'LALPATHLAB.NS', 'LICHSGFIN.NS', 'LT.NS', 'LTIM.NS', 'LUPIN.NS',
    'M&M.NS', 'M&MFIN.NS', 'MANAPPURAM.NS', 'MARICO.NS', 'MARUTI.NS', 'MCDOWELL-N.NS',
    'MCX.NS', 'METROBRAND.NS', 'MGL.NS', 'MINDTREE.NS', 'MPL.NS', 'MRF.NS',
    'MUTHOOTFIN.NS', 'NAM-INDIA.NS', 'NATCOPHARM.NS', 'NAVINFLUOR.NS', 'NBCC.NS', 'NCC.NS',
    'NESTLEIND.NS', 'NMDC.NS', 'NTPC.NS', 'OBEROIRLTY.NS', 'OFSS.NS', 'OIL.NS',
    'ONGC.NS', 'PAGEIND.NS', 'PEL.NS', 'PETRONET.NS', 'PFC.NS', 'PIDILITIND.NS',
    'PNB.NS', 'POLYCAB.NS', 'POWERGRID.NS', 'PRESTIGE.NS', 'PTC.NS', 'RAMCOCEM.NS',
    'RBLBANK.NS', 'RECLTD.NS', 'RELIANCE.NS', 'SAIL.NS', 'SBICARD.NS', 'SBILIFE.NS',
    'SBIN.NS', 'SHREECEM.NS', 'SIEMENS.NS', 'SRF.NS', 'SRTRANSFIN.NS', 'STARHEALTH.NS',
    'SUNPHARMA.NS', 'SUNTV.NS', 'SUPREMEIND.NS', 'SYNGENE.NS', 'TATACHEM.NS', 'TATACONSUM.NS',
    'TATAMOTORS.NS', 'TATAPOWER.NS', 'TATASTEEL.NS', 'TCS.NS', 'TECHM.NS', 'TITAN.NS',
    'TORNTPHARM.NS', 'TORNTPOWER.NS', 'TRENT.NS', 'TVSMOTOR.NS', 'UBL.NS', 'ULTRACEMCO.NS',
    'UPL.NS', 'VEDL.NS', 'VOLTAS.NS', 'WHIRLPOOL.NS', 'WIPRO.NS', 'YESBANK.NS',
    'ZYDUSLIFE.NS'
]

    # Dictionary to store stock data
      data = {}

    # Fetch data for today's date (1-minute intervals)
    for symbol in symbols:
        stock_data = yf.download(symbol, period="1d", interval="1m")  # Fetching 1-minute intervals
        data[symbol] = stock_data

    # List to store calculated gains and losses
    gainers_losers = []

    # Calculate the percentage change from the first price to the last price of the day
    for symbol, stock_data in data.items():
        if not stock_data.empty:
            # Check if data exists
            open_price = stock_data.iloc[0]['Open']
            close_price = stock_data.iloc[-1]['Close']
            percent_change = ((close_price - open_price) / open_price) * 100
            gainers_losers.append({'Symbol': symbol, 'Change (%)': percent_change})

    # Create a DataFrame
    df_gainers_losers = pd.DataFrame(gainers_losers)

    # Ensure the 'Change (%)' column is numeric (force conversion)
    df_gainers_losers['Change (%)'] = pd.to_numeric(df_gainers_losers['Change (%)'], errors='coerce')

    # Drop any rows with NaN values in case there are any
    df_gainers_losers = df_gainers_losers.dropna(subset=['Change (%)'])

    # Sort the DataFrame by Change (%), descending for gainers and ascending for losers
    df_gainers_losers = df_gainers_losers.sort_values(by='Change (%)', ascending=False)

    # Get top 5 gainers and losers
    top_5_gainers = df_gainers_losers.head(5)
    top_5_losers = df_gainers_losers.tail(5)

    return top_5_gainers, top_5_losers

# Streamlit UI setup
def display_dashboard():
    # Title and sidebar title
    st.sidebar.title("Stock Market Dashboard")
    st.title("Today's Top Gainers and Losers")

    # Fetch today's top gainers and losers
    top_5_gainers, top_5_losers = get_top_gainers_losers()

    # Display Top 5 Gainers
    st.write("### Top 5 Gainers Today")
    st.write(top_5_gainers)

    # Display Top 5 Losers
    st.write("### Top 5 Losers Today")
    st.write(top_5_losers)

# Main app execution
if __name__ == "__main__":
    display_dashboard()
# --------- Select Stock to View Chart ---------
st.subheader("📊 Stock Price Chart")
selected_symbol = st.selectbox("Select a stock to visualize", symbols)
data = fetch_stock_data(selected_symbol, datetime.now() - timedelta(days=30), datetime.now())

if not data.empty:
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close']
    )])
    fig.update_layout(title=f"{selected_symbol} - Last 30 Days", xaxis_title="Date", yaxis_title="Price (INR)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available for the selected stock.")

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

