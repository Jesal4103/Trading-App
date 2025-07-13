import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import pandas_datareader.data as web
from pages.utils.CAPM_func import interactive_plot
from pages.utils.CAPM_func import normalize
from pages.utils.CAPM_func import daily_return
from pages.utils.CAPM_func import calulate_beta

st.set_page_config(
    page_title="CAPM",
    page_icon="chart_with_downwards_trend",
    layout="wide"
)
st.title("Capital Asset Pricing Model")

# User Input
col1, col2 = st.columns([1, 1])
with col1:
    stocks_list = st.multiselect(
        "Choose 4 stocks",
        ('TSLA', 'AAPL', 'MGM', 'MSFT', 'NFLX', 'AMZN', 'NVDA', 'GOOGL'),
        ['TSLA', 'AAPL', 'NFLX', 'GOOGL']
    )
with col2:
    year = st.number_input("Number of years", 1, 10)

# Date range
try:
    end = datetime.date.today()
    start = datetime.date(end.year - year, end.month, end.day)

    # Download SP500 Data
    SP500 = web.DataReader('SP500', 'fred', start, end)
    SP500 = SP500.reset_index()
    SP500.columns = ['Date', 'sp500']
    SP500['Date'] = pd.to_datetime(SP500['Date'])

    # Download stock data and combine
    stock_data_list = []

    for stock in stocks_list:
        df = yf.download(stock, start=start, end=end)[['Close']]
        df = df.rename(columns={'Close': stock})
        stock_data_list.append(df)

    # Combine stock close prices on the index (which is Date)
    combined_stocks = pd.concat(stock_data_list, axis=1, join='inner')

    # Reset index and flatten completely
    combined_stocks = combined_stocks.reset_index()  # Makes 'Date' a column
    combined_stocks['Date'] = pd.to_datetime(combined_stocks['Date'])

    # Ensure no MultiIndex remains
    combined_stocks.columns = [col if isinstance(col, str) else col[0] for col in combined_stocks.columns]

    # Merge with SP500 data
    merged_df = pd.merge(combined_stocks, SP500, on='Date', how='inner')

    # Display result
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Dataframe Head")
        st.dataframe(merged_df.head(), use_container_width=True)
    with col2:
        st.markdown("### Dataframe Tail")
        st.dataframe(merged_df.tail(), use_container_width=True)

    col1, col2=st.columns([1,1])
    with col1:
        st.markdown("### Price of all the Stocks")
        st.plotly_chart(interactive_plot(merged_df))
    with col2:
        st.markdown("### Price of Stocks (After Normalizing)")
        st.plotly_chart(interactive_plot(normalize(merged_df)))

    stock_daily_return=daily_return(merged_df)
    print(stock_daily_return.head())

    beta={}
    alpha={}

    for i in stock_daily_return.columns:
        if i!='Date' and i!='SP500':
            b,a = calulate_beta(stock_daily_return,i)
            beta[i]=b
            alpha[i]=a
    print(beta,alpha)
        
    beta_df=pd.DataFrame(columns=['Stock', 'Beta Value'])
    beta_df['Stock']=beta.keys()
    beta_df['Beta Value']=[str(round(i,2)) for i in beta.values()]

    with col1:
        st.markdown("### Calculated Beta Value")
        st.dataframe(beta_df, use_container_width=True)

    rf = 0
    rm = stock_daily_return['sp500'].mean() * 252
    return_df = pd.DataFrame()
    return_value = []

    for stock, value in beta.items():
        return_value.append(str(round(rf + (value * (rm - rf)), 2)))

    return_df['Stock'] = list(beta.keys())  # Match exactly with return_value
    return_df['Return Value'] = return_value


    with col2:
        st.markdown("### Calculated return using CAPM")
        st.dataframe(return_df, use_container_width=True)

except:
    st.write("Please Select Valid Tickers")
