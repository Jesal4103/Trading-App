import streamlit as st
import pandas as pd
from pages.utils.model_train import (
    get_data, get_rolling_mean, get_differencing_order,
    fit_model, evaluate_model, get_forecast
)
from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

st.set_page_config(
    page_title="Stock Prediction",
    page_icon="📉",
    layout="wide",
)

st.title("📈 Stock Prediction")

col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("Enter the Stock Ticker", 'TSLA')

st.subheader(f"Predicting the Close Price over the next 30 days for: {ticker}")

@st.cache_data(ttl=3600)
def load_data(ticker):
    return get_data(ticker)

@st.cache_data(ttl=3600)
def preprocess(data):
    rolling = get_rolling_mean(data)
    d = get_differencing_order(rolling)
    return rolling, d

@st.cache_resource(ttl=3600)
def train_once(data_series, d):
    rmse = evaluate_model(data_series, d)
    model_fit = fit_model(data_series, d)
    return rmse, model_fit

# Main logic
close_price = load_data(ticker)
rolling_price, differencing_order = preprocess(close_price)

# Convert rolling_price to tuple (required for caching via lru_cache)
data_tuple = tuple(rolling_price['Close'].values)

rmse, model_fit = train_once(data_tuple, differencing_order)
forecast_df = get_forecast(model_fit)

st.write("**Model RMSE Score:**", rmse)

st.write("### Forecast Data (Next 30 days)")
fig_table = plotly_table(forecast_df.round(2))
fig_table.update_layout(height=220)
st.plotly_chart(fig_table, use_container_width=True)

# Combine and visualize
merged = pd.concat([rolling_price, forecast_df])
st.plotly_chart(
    Moving_average_forecast(merged.iloc[-60:]),
    use_container_width=True
)
