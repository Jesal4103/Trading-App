import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import pandas_datareader.data as web
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np

# ---------- Page Config ----------
st.set_page_config(
    page_title="Beta and Return Calculator",
    page_icon="📈",
    layout="wide"
)

st.markdown("## Calculate Beta and Return for Individual Stock")

# ---------- User Inputs ----------
col1, col2 = st.columns([1, 1])
with col1:
    stock_ticker = st.text_input("Choose a stock", value="TSLA").upper()

with col2:
    years = st.number_input("Number of Years", min_value=1, max_value=10, value=1)

# ---------- Date Range ----------
end = datetime.date.today()
start = datetime.date(end.year - years, end.month, end.day)

# ---------- Data Download ----------
@st.cache_data
def download_data(ticker, start_date, end_date):
    try:
        # Download stock data
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        stock_data = stock_data[['Close']].rename(columns={'Close': 'Stock'})
        
        # Download S&P 500 data
        sp500_data = web.DataReader('SP500', 'fred', start_date, end_date)
        sp500_data = sp500_data.rename(columns={'SP500': 'SP500'})
        
        return stock_data, sp500_data
    except Exception as e:
        st.error(f"Error downloading data: {e}")
        return None, None

stock_data, sp500_data = download_data(stock_ticker, start, end)

if stock_data is None or sp500_data is None:
    st.stop()

# ---------- Data Alignment ----------
def align_data(stock_df, sp500_df):
    # Convert to DataFrames if they're Series
    if isinstance(stock_df, pd.Series):
        stock_df = stock_df.to_frame('Stock')
    if isinstance(sp500_df, pd.Series):
        sp500_df = sp500_df.to_frame('SP500')
    
    # Ensure we have proper column names
    stock_df.columns = ['Stock']
    sp500_df.columns = ['SP500']
    
    # Convert indices to datetime and normalize
    stock_df.index = pd.to_datetime(stock_df.index).normalize()
    sp500_df.index = pd.to_datetime(sp500_df.index).normalize()
    
    # Merge using index alignment
    combined = pd.concat([stock_df, sp500_df], axis=1).dropna()
    
    return combined

df = align_data(stock_data, sp500_data)

if df.empty:
    st.error("No overlapping data found between stock and S&P 500")
    st.stop()

# ---------- Calculate Returns ----------
df['stock_return'] = df['Stock'].pct_change() * 100
df['sp500_return'] = df['SP500'].pct_change() * 100
df = df.dropna()

# ---------- Calculate Beta ----------
X = df['sp500_return'].values.reshape(-1, 1)
y = df['stock_return'].values.reshape(-1, 1)

model = LinearRegression()
model.fit(X, y)
beta = float(model.coef_[0])
alpha = float(model.intercept_[0])

# ---------- Calculate Expected Return ----------
rf = 0  # risk-free rate
rm = df['sp500_return'].mean() * 252  # annualized market return
expected_return = rf + beta * (rm - rf)

# ---------- Display Results ----------
col1, col2 = st.columns(2)
with col1:
    st.metric("Beta", value=f"{beta:.4f}")

with col2:
    st.metric("Expected Annual Return", value=f"{expected_return:.2f}%")

# ---------- Create Scatter Plot ----------
fig = go.Figure()

# Scatter plot of returns
fig.add_trace(go.Scatter(
    x=df['sp500_return'],
    y=df['stock_return'],
    mode='markers',
    marker=dict(color='lightblue', size=8),
    name='Daily Returns'
))

# Regression line
x_range = np.linspace(df['sp500_return'].min(), df['sp500_return'].max(), 100)
y_range = beta * x_range + alpha
fig.add_trace(go.Scatter(
    x=x_range,
    y=y_range,
    mode='lines',
    line=dict(color='red', width=2),
    name=f'Regression Line (β={beta:.2f})'
))

# Layout configuration with black background and visible scales
fig.update_layout(
    title=f'{stock_ticker} vs S&P 500 Daily Returns',
    xaxis_title='S&P 500 Daily Return (%)',
    yaxis_title=f'{stock_ticker} Daily Return (%)',
    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(color='white'),
    xaxis=dict(
        showline=True,
        linecolor='white',
        gridcolor='rgba(255,255,255,0.1)',
        zerolinecolor='rgba(255,255,255,0.5)',
        tickfont=dict(color='white')
    ),
    yaxis=dict(
        showline=True,
        linecolor='white',
        gridcolor='rgba(255,255,255,0.1)',
        zerolinecolor='rgba(255,255,255,0.5)',
        tickfont=dict(color='white')
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(color='white')
    ),
    hovermode='closest'
)

# Add scale/axis information
fig.add_annotation(
    x=0.05,
    y=0.95,
    xref="paper",
    yref="paper",
    text=f"Scale: X-Axis (S&P 500) ±{df['sp500_return'].abs().max():.1f}%, Y-Axis ({stock_ticker}) ±{df['stock_return'].abs().max():.1f}%",
    showarrow=False,
    font=dict(color='white', size=12),
    bgcolor='rgba(0,0,0,0.7)',
    bordercolor='white'
)

# Display the plot
st.plotly_chart(fig, use_container_width=True)