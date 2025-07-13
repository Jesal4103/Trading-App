import yfinance as yf
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from functools import lru_cache

def get_data(ticker):
    stock_data = yf.download(ticker, start='2024-01-01')
    return stock_data[['Close']]

def stationary_check(close_price):
    adf_test = adfuller(close_price)
    return round(adf_test[1], 3)

def get_rolling_mean(close_price):
    return close_price.rolling(window=7).mean().dropna()

def get_differencing_order(close_price):
    p = stationary_check(close_price)
    d = 0
    while p > 0.05 and d < 3:  # cap differencing
        d += 1
        close_price = close_price.diff().dropna()
        p = stationary_check(close_price)
    return d

@lru_cache(maxsize=5)
def fit_model(data_tuple, d):
    data = pd.Series(data_tuple)
    model = ARIMA(data, order=(5, d, 5))  # optimized order
    return model.fit()

def evaluate_model(data_tuple, d):
    data = pd.Series(data_tuple)
    train, test = data[:-30], data[-30:]
    model = ARIMA(train, order=(5, d, 5)).fit()
    preds = model.get_forecast(steps=30).predicted_mean
    return round(np.sqrt(mean_squared_error(test, preds)), 2)

def get_forecast(model_fit):
    forecast_steps = 30
    preds = model_fit.get_forecast(steps=forecast_steps).predicted_mean
    dates = pd.date_range(datetime.now(), periods=30)
    return pd.DataFrame({'Close': preds}, index=dates)
