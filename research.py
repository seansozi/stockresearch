import streamlit as st, pandas as pd, numpy as np, yfinance as yf
import plotly.express as px
import base64
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request


st.title("Stocks Dashboard")

ticker = st.selectbox('Select Ticker',('BYON', 'AAPL'))

ratings = {
    'AAPL': 'Hold',
    'BYON': 'Buy',
}

# Display the rating
if ticker in ratings:
    st.subheader(f'Maxim Rating: {ratings[ticker]}')
else:
    st.subheader('Rating: Not Available')

start_date = st.sidebar.date_input('Start date', value=pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input('End date', value=pd.to_datetime("today"))

data = yf.download(ticker, start = start_date, end = end_date)
data['% Change'] = data['Adj Close'].pct_change() * 100
data_reversed = data.iloc[::-1]


fig = px.line(data, x = data.index, y = data ['Adj Close'], title = ticker)
st.plotly_chart(fig)


#Maxim report

ticker_pdf_mapping = {
    'AAPL': {'file_name': 'AAPL_report.pdf', 'file_url': 'https://maxim.bluematrix.com/sellside/EmailDocViewer?encrypt=b1459a90-e146-434d-bb73-c1ad6ff88004&mime=pdf&co=maxim&id=tforte@maximgrp.com&source=mailf'},
    'BYON': {'file_name': 'BYON_report.pdf', 'file_url': 'https://maxim.bluematrix.com/sellside/EmailDocViewer?encrypt=ed9c8963-d9bc-4ab4-a4df-7aac0bb7ae0e&mime=pdf&co=maxim&id=tforte@maximgrp.com&source=mailf'}
}
ticker_data = ticker_pdf_mapping.get(ticker)


news, maxim_report, pricing_data, fundamental_data, = st.tabs(['News & Sentiement Analysis', 'Latest Maxim Report', 'Pricing Data', 'Fundamental Analysis'])

api_key = "8VCEC6hJuyQuYDVNlvFpGwJCcnBaqudG"


with maxim_report:
    st.header('Maxim Group Report')
    pdf_url = ticker_data.get('file_url')
    st.write(pdf_url)

with pricing_data:
  st.header('Price Movements')
  st.write(data_reversed)
  selected_start_date = pd.to_datetime(start_date)
  selected_end_date = pd.to_datetime(end_date)
  total_return = (data['Adj Close'].iloc[-1] - data['Adj Close'].iloc[0]) / data['Adj Close'].iloc[0]
  years_in_period = (selected_end_date - selected_start_date).days / 365
  annualized_return = (total_return + 1) ** (1 / years_in_period) - 1
  annualized_return_percent = annualized_return * 100
  st.write(f'Annualized Return over the selected period is: {annualized_return_percent:.2f}%')
  std_deviation = data['Adj Close'].std()
  st.write(f'Standard Deviation of Adj Close Prices: {std_deviation:.2f}')

with fundamental_data:
    st.header('Fundamental Data')
    fundamental_url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?apikey={api_key}"
    fundamental_data = requests.get(fundamental_url).json()
    metrics_df = pd.DataFrame(fundamental_data)
    transposed_metrics_df = metrics_df.T

    st.write(transposed_metrics_df)

with news:
    # Fetch news data
    news_data = []
    for page in range(1, 3):  # Assuming you have access to 5 pages based on your plan
        news_url = f'https://stocknewsapi.com/api/v1?tickers={ticker}&items=2&page={page}&token=ibropa3f2tlngvbvowwzliy3udueqotah3nfbrz1'
        news_response = requests.get(news_url)
        news_data.extend(news_response.json().get('data', []))   
        
    # Display news data in a user-friendly format
    st.title("Stock News")
    st.write(f"Showing news for {ticker}")

    for item in news_data:
        st.subheader(item['title'])
        st.write(f"Source: {item['source_name']}")
        st.write(f"Date: {item['date']}")
        st.write(f"Sentiment: {item['sentiment']}")
        st.image(item['image_url'], caption='Image', use_column_width=True)
        st.write(item['text'])
        st.write(f"Read more: [{item['source_name']}]({item['news_url']})")
