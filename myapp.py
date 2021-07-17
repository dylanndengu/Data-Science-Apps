import yfinance as yf
import streamlit as st
import pandas as pd
import datetime

st.title('Dylan\'s Yahoo Stock Price App')
st.write("""

Shown are the stock closing price, volume and recommendations

""")


#Sidebar

stock_options = st.sidebar.selectbox('Select A Symbol', ('GOOGL','AAPL', 'MSFT',"SPY",'WMT'))

start_date = st.sidebar.date_input('Start Date', value = datetime.date.today()-datetime.timedelta(days=1800))
end_date = st.sidebar.date_input('End Date', value = datetime.date.today())

if start_date > end_date:
    st.sidebar.error('Error : Start Date must be before End Date')



#Main Body

tickerSymbol = stock_options

tickerData = yf.Ticker(tickerSymbol)

recommendations = tickerData.recommendations

tickerDf = tickerData.history(period='1d', start=start_date, end=end_date)

st.line_chart(tickerDf.Close)
st.area_chart(tickerDf.Volume)
st.write(recommendations)

