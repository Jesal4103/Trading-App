import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import datetime
import ta
from pages.utils.plotly_figure import plotly_table
from pages.utils.plotly_figure import filter_data
from pages.utils.plotly_figure import close_chart
from pages.utils.plotly_figure import candlestick
from pages.utils.plotly_figure import RSI
from pages.utils.plotly_figure import Moving_average
from pages.utils.plotly_figure import plot_MACD

st.set_page_config(
    page_title="Stock Analysis",
    page_icon="📄",
    layout="wide",
)

# Extremely aggressive CSS to reduce all spacing
st.markdown("""
    <style>
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
    }
    .element-container {
        margin-bottom: 0rem !important;
        padding-bottom: 0rem !important;
    }
    div[data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.1);
        padding: 5px !important;
        border-radius: 5px;
        margin: 0 !important;
    }
    div[data-testid="metric-container"] > div {
        padding: 0 !important;
        margin: 0 !important;
    }
    div[data-testid="stMetricValue"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    div[data-testid="stMetricDelta"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    .stPlotlyChart {
        margin: 0 !important;
        padding: 0 !important;
    }
    h1, h2, h3, h4, h5 {
        margin-top: 0.2rem !important;
        margin-bottom: 0.1rem !important;
    }
    .stDataFrame {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }
    .css-1y4p8pa {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
    }
    .css-1v0mbdj {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }
    .stMarkdown {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Stock Analysis")

available_tickers = [
    "AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NVDA", "META", "NFLX", "BRK-B", "JPM"
]

col1, col2, col3 = st.columns(3)
today = datetime.date.today()

with col1:
    ticker = st.selectbox("Select Stock Ticker", options=available_tickers, index=3)
with col2:
    start_date = st.date_input("Choose Start Date", datetime.date(today.year - 1, today.month, today.day))
with col3:
    end_date = st.date_input("Choose End Date", today)

st.subheader(ticker)

# Load stock
stock = yf.Ticker(ticker)
info = stock.info

# Business summary with minimal spacing
st.write(info.get('longBusinessSummary', 'No business summary available.'))
cols = st.columns(3)
with cols[0]:
    st.write("**Sector:**", info.get('sector', 'N/A'))
with cols[1]:
    st.write("**Full Time Employees:**", info.get('fullTimeEmployees', 'N/A'))
with cols[2]:
    st.write("**Know More:**", info.get('website', 'N/A'))

# Financial metrics in a single row with minimal spacing
metrics_row = st.columns([1, 1, 0.5, 1, 1])  # Added a small spacer column

with metrics_row[0]:
    df1 = pd.DataFrame({
        'Metric': ['Beta', 'EPS', 'PE Ratio'],
        'Value': [
            info.get('beta', 'N/A'),
            info.get('trailingEps', 'N/A'),
            info.get('trailingPE', 'N/A')
        ]
    })
    st.dataframe(df1.set_index('Metric'), height=150)

with metrics_row[1]:
    df2 = pd.DataFrame({
        'Metric': ['Current Ratio', 'Revenue Per Share', 'Debt to Equity'],
        'Value': [
            info.get("currentRatio", 'N/A'),
            info.get("revenuePerShare", 'N/A'),
            info.get("debtToEquity", 'N/A')
        ]
    })
    st.dataframe(df2.set_index('Metric'), height=150)

# Daily close and last 10 days data in a tight layout
try:
    data = yf.download(ticker, start=start_date, end=end_date)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if len(data) < 2:
        st.warning("Not enough historical data available to show daily change.")
    else:
        # Extremely tight layout for daily close and table
        daily_col, table_col = st.columns([1, 3])
        
        with daily_col:
            latest_close = float(data['Close'].iloc[-1])
            prev_close = float(data['Close'].iloc[-2])
            daily_change = latest_close - prev_close
            st.metric("Daily Close", f"{latest_close:.2f}", f"{daily_change:.2f}")
            st.write("")  # Minimal spacer

        with table_col:
            st.markdown("**Data of the Last 10 Days**")
            last_10_df = data.tail(10).sort_index(ascending=False).round(3)
            st.dataframe(last_10_df)
            
except Exception as e:
    st.error(f"Error loading stock data: {e}")

# Time period buttons - single line with minimal spacing
period_cols = st.columns([1,1,1,1,1,1,1,1,1,1,1,1])
num_period = ''
with period_cols[0]:
    if st.button('5D', key='5d'):
        num_period = '5D'
with period_cols[1]:
    if st.button('1M', key='1m'):
        num_period = '1mo'
with period_cols[2]:
    if st.button('6M', key='6m'):
        num_period = '6mo'
with period_cols[3]:
    if st.button('YTD', key='ytd'):
        num_period = 'ytd'
with period_cols[4]:
    if st.button('1Y', key='1y'):
        num_period = '1y'
with period_cols[5]:
    if st.button('5Y', key='5y'):
        num_period = '5y'
with period_cols[6]:
    if st.button('MAX', key='max'):
        num_period = 'max'

# Chart selection with minimal spacing
chart_cols = st.columns([1, 1, 4])
with chart_cols[0]:
    chart_type = st.selectbox('Chart Type', ['Line', 'Candle'])
with chart_cols[1]:
    if chart_type == 'Candle':
        indicator = st.selectbox('Indicator', ['RSI', 'MACD'])
    else:
        indicator = st.selectbox('Indicator', ['RSI', 'Moving Average', 'MACD'])

# Charts with minimal spacing
st.markdown("### Main Chart")
data_used = stock.history(period=num_period if num_period else '1y')
period_used = num_period if num_period else '1y'

if chart_type == 'Candle':
    st.plotly_chart(candlestick(data_used, period_used), use_container_width=True)
else:
    st.plotly_chart(close_chart(data_used, period_used), use_container_width=True)

st.markdown("### Indicator Chart")
if indicator == 'RSI':
    st.plotly_chart(RSI(data_used, period_used), use_container_width=True)
elif indicator == 'Moving Average':
    st.plotly_chart(Moving_average(data_used, period_used), use_container_width=True)
elif indicator == 'MACD':
    st.plotly_chart(plot_MACD(data_used, period_used), use_container_width=True)