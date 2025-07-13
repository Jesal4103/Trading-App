import dateutil.relativedelta
import plotly.graph_objects as go
import ta
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import pandas as pd
import yfinance as yf
import datetime
import dateutil

# Plotly Table Function
def plotly_table(dataframe):
    headerColor = '#1f2c56'
    rowEvenColor = '#2e3b5f'
    rowOddColor = '#1c253b'

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b>Index</b>"] + ["<b>"+str(i)+"</b>" for i in dataframe.columns],
            line_color=headerColor, fill_color='#3f4c6b',
            align='center', font=dict(color='white', size=15), height=35
        ),
        cells=dict(
            values=[[f"<b>{i}</b>" for i in dataframe.index]] + [dataframe[col] for col in dataframe.columns],
            fill_color=[rowOddColor if i % 2 == 0 else rowEvenColor for i in range(len(dataframe))],
            align='left', line_color='white',
            font=dict(color="white", size=14)
        )
    )])

    fig.update_layout(height=600, margin=dict(l=0, r=0, t=0, b=0))
    return fig

def filter_data(dataframe, num_period):
    if num_period == '1mo':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(months=-1)
    elif num_period == '5d':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(days=-5)
    elif num_period == '6mo':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(months=-6)
    elif num_period == '1y':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(years=-1)
    elif num_period == '5y':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(years=-5)
    elif num_period == 'ytd':
        date = datetime.datetime(dataframe.index[-1].year, 1, 1).strftime('%Y-%m-%d')
    else:
        date = dataframe.index[0]

    return dataframe.reset_index()[dataframe.reset_index()['Date'] > date]

def close_chart(dataframe, num_period=False):
    if num_period:
        dataframe = filter_data(dataframe, num_period)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=dataframe['Open'],
        mode='lines',
        name='Open',
        line=dict(width=2, color='#5ab7ff')
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=dataframe['Close'],
        mode='lines',
        name='Close',
        line=dict(width=2, color='black')
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=dataframe['High'],
        mode='lines',
        name='High',
        line=dict(width=2, color='#0078ff')
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=dataframe['Low'],
        mode='lines',
        name='Low',
        line=dict(width=2, color='red')
    ))

    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(
        height=500,
        margin=dict(l=0, r=20, t=20, b=0),
        plot_bgcolor='black',
        paper_bgcolor='#e1efff',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(
                size=14,
                color="black"
            )
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(color='black')
        )
    )

    return fig

def candlestick(dataframe, num_period):
    dataframe = filter_data(dataframe, num_period)
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=dataframe['Date'],
        open=dataframe['Open'],
        high=dataframe['High'],
        low=dataframe['Low'],
        close=dataframe['Close']
    ))

    fig.update_layout(
        showlegend=False,
        height=500,
        margin=dict(l=0, r=20, t=20, b=0),
        plot_bgcolor='black',
        paper_bgcolor='#e1efff',
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(color='black')
        )
    )
    return fig

def RSI(dataframe, num_period):
    if num_period:
        dataframe = filter_data(dataframe, num_period)

    rsi = RSIIndicator(close=dataframe['Close'], window=14)
    dataframe['RSI'] = rsi.rsi()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=dataframe['RSI'],
        name='RSI',
        mode='lines',
        marker_color='orange',
        line=dict(width=2, color='orange')
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=[70]*len(dataframe),
        name='Overbought',
        mode='lines',
        marker_color='red',
        line=dict(width=2, color='red', dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=[30]*len(dataframe),
        name='Oversold',
        mode='lines',
        marker_color='#79da84',
        line=dict(width=2, color='#79da84', dash='dash')
    ))

    fig.update_layout(
        yaxis_range=[0, 100],
        height=200,
        plot_bgcolor='black',
        paper_bgcolor='#e1efff',
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(
                color='black'
            )
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(color='black')
        )
    )
    return fig

def Moving_average(dataframe, num_period):
    sma = SMAIndicator(close=dataframe['Close'], window=50)
    dataframe['SMA_50'] = sma.sma_indicator()

    dataframe = filter_data(dataframe, num_period)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=dataframe['Open'],
        mode='lines', name='Open',
        line=dict(width=2, color='#5ab7ff')
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=dataframe['Close'],
        mode='lines', name='Close',
        line=dict(width=2, color='black')
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=dataframe['High'],
        mode='lines', name='High',
        line=dict(width=2, color='#0078ff')
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=dataframe['Low'],
        mode='lines', name='Low',
        line=dict(width=2, color='red')
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=dataframe['SMA_50'],
        mode='lines', name='SMA 50',
        line=dict(width=2, color='purple')
    ))

    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(
        height=500,
        margin=dict(l=0, r=20, t=20, b=0),
        plot_bgcolor='black',
        paper_bgcolor='#e1efff',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(
                color='black'
            )
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(color='black')
        )
    )
    return fig

def plot_MACD(dataframe, num_period):
    macd = MACD(close=dataframe['Close'])
    dataframe['MACD'] = macd.macd()
    dataframe['MACD Signal'] = macd.macd_signal()
    dataframe['MACD Hist'] = macd.macd_diff()

    dataframe = filter_data(dataframe, num_period)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dataframe['Date'],
        y=dataframe['MACD'],
        name='MACD',
        mode='lines',
        line=dict(width=2, color='orange')
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Date'],
        y=dataframe['MACD Signal'],
        name='Signal',
        mode='lines',
        line=dict(width=2, color='red', dash='dash')
    ))

    bar_colors = ['green' if val >= 0 else 'red' for val in dataframe['MACD Hist']]
    fig.add_trace(go.Bar(
        x=dataframe['Date'],
        y=dataframe['MACD Hist'],
        name='Histogram',
        marker_color=bar_colors
    ))

    fig.update_layout(
        height=200,
        plot_bgcolor='black',
        paper_bgcolor='#e1efff',
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(
                color='black'
            )
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(color='black')
        )
    )
    return fig

import plotly.graph_objects as go

def Moving_average_forecast(forecast):
    fig = go.Figure()

    # Actual Close Price
    fig.add_trace(go.Scatter(
        x=forecast.index[:-30], 
        y=forecast['Close'].iloc[:-30],
        mode='lines',
        name='Close Price', 
        line=dict(width=2, color='black')
    ))

    # Forecasted Close Price
    fig.add_trace(go.Scatter(
        x=forecast.index[-31:], 
        y=forecast['Close'].iloc[-31:],
        mode='lines', 
        name='Future Close Price', 
        line=dict(width=2, color='red')
    ))

    # Update axes with scales
    fig.update_xaxes(
        title_text="Date",
        showgrid=True,
        showline=True,
        ticks="outside",
        showticklabels=True,
        linecolor='black',
        tickfont=dict(color='black'),
        title_font=dict(color='black')
    )
    fig.update_yaxes(
        title_text="Close Price",
        showgrid=True,
        showline=True,
        ticks="outside",
        showticklabels=True,
        linecolor='black',
        tickfont=dict(color='black'),
        title_font=dict(color='black')
    )

    # Layout customization
    fig.update_layout(
        height=500,
        margin=dict(l=0, r=20, t=20, b=0), 
        plot_bgcolor='black',
        paper_bgcolor='#e1efff',
        legend=dict(
            yanchor="top",
            xanchor="right",
            font=dict(color='black')  # Legend font color
        ),
        xaxis_rangeslider_visible=True
    )

    return fig
