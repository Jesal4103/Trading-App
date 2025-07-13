import plotly.express as px
import numpy as np

#function to plaot interactive chart

def interactive_plot(df):
    fig=px.line()
    for i in df.columns[1:]:
        fig.add_scatter(x=df['Date'], y=df[i], name=i)
    fig.update_layout(width=450, margin=dict(l=20, r=20, t=50, b=20), legend=dict(orientation='h', yanchor='top', y=1.02, xanchor='right', x=1))
    return fig

# Normalization function to normalize the price of the stocks based on initial price
def normalize(df_2):
    df=df_2.copy()
    for i in df.columns[1:]:
        df[i]=df[i]/df[i][0]
    return df

# Functions to create daily returns
def daily_return(df):
    df_daily_return=df.copy()
    for i in df_daily_return.columns[1:]:
        for j in range(1,len(df)):
            df_daily_return[i][j]=((df_daily_return[i][j]-df_daily_return[i][j-1])/df_daily_return[i][j-1])*100
        df_daily_return[i][0]=0
    return df_daily_return

# function to calculate beta
def calulate_beta(stock_daily_return, stock):
    rm=stock_daily_return['sp500'].mean()*252
    b,a=np.polyfit(stock_daily_return['sp500'], stock_daily_return[stock],1)
    return b,a