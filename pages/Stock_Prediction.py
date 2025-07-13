import streamlit as st
import pandas as pd
from pages.utils.model_train import get_data
from pages.utils.model_train import stationary_check
from pages.utils.model_train import get_rolling_mean
from pages.utils.model_train import get_differencing_order
from pages.utils.model_train import fit_model
from pages.utils.model_train import evaluate_model
from pages.utils.model_train import scaling
from pages.utils.model_train import get_forecast
from pages.utils.model_train import inverse_scaling
from pages.utils.plotly_figure import plotly_table
from pages.utils.plotly_figure import Moving_average_forecast

st.set_page_config(
    page_title="Stock Prediction",
    page_icon="chart_with_downwards_trend",
    layout="wide",
)

st.title("Stock Prediction")
col1, col2, col3 = st.columns(3)

with col1:
    ticker=st.text_input("Enter the Stock Ticker", 'TSLA')
rmse=0

st.subheader("Predicting the Close Price over the next 30 days for:"+ticker)

close_price=get_data(ticker)
rolling_price=get_rolling_mean(close_price)

differencing_order = get_differencing_order(rolling_price)
scaled_data, scaler = scaling(rolling_price)
rmse = evaluate_model(scaled_data, differencing_order)

st.write("**Model RMSE Score:**", rmse)

forecast = get_forecast(scaled_data, differencing_order)

forecast['Close'] = inverse_scaling(scaler, forecast['Close'])
st.write('### Forecast Data (Next 30 days)')
fig_tail = plotly_table(forecast.sort_index(ascending=True).round(3))
fig_tail.update_layout(height=220)
st.plotly_chart(fig_tail, use_container_width=True)

forecast = pd.concat([rolling_price, forecast])

st.plotly_chart(Moving_average_forecast(forecast.iloc[100:]), use_container_width=True)

