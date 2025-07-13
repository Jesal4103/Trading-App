import streamlit as st
import pandas as pd
from pages.utils.model_train import (
    get_data, stationary_check, get_rolling_mean, get_differencing_order,
    fit_model, evaluate_model, scaling, get_forecast, inverse_scaling
)
from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

st.set_page_config(
    page_title="Stock Prediction",
    page_icon="chart_with_downwards_trend",
    layout="wide",
)

st.title("Stock Prediction")
col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input("Enter the Stock Ticker", 'TSLA')

st.subheader(f"Predicting the Close Price over the next 30 days for: {ticker}")

@st.cache_data(ttl=3600)
def load_close_price(ticker):
    return get_data(ticker)

@st.cache_data(ttl=3600)
def preprocess_data(close_price):
    rolling = get_rolling_mean(close_price)
    order = get_differencing_order(rolling)
    scaled, scaler = scaling(rolling)
    return rolling, scaled, scaler, order

@st.cache_resource(ttl=3600)
def train_and_forecast(scaled_data, order):
    rmse = evaluate_model(scaled_data, order)
    forecast = get_forecast(scaled_data, order)
    return rmse, forecast

# Main logic
close_price = load_close_price(ticker)
rolling_price, scaled_data, scaler, differencing_order = preprocess_data(close_price)
rmse, forecast = train_and_forecast(scaled_data, differencing_order)

# Post-processing
forecast['Close'] = inverse_scaling(scaler, forecast['Close'])

st.write("**Model RMSE Score:**", rmse)

st.write('### Forecast Data (Next 30 days)')
fig_tail = plotly_table(forecast.round(3))
fig_tail.update_layout(height=220)
st.plotly_chart(fig_tail, use_container_width=True)

# Final Visualization
merged_forecast = pd.concat([rolling_price, forecast])
st.plotly_chart(
    Moving_average_forecast(merged_forecast.iloc[-60:]),  # Limit to last 60 rows
    use_container_width=True
)
