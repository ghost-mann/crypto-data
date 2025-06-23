import requests
import pandas as pd
import time

BASE_URL = "https://api.binance.com"

def get_latest_prices():
    url = f'{BASE_URL}/api/v3/ticker/price'
    response = requests.get(url)
    data = response.json()
    df_prices = pd.DataFrame(data)
    print(df_prices)
    return df_prices
    
def order_book(symbol='BTCUSDT',limit=5):
    url = f'{BASE_URL}/api/v3/depth'
    params = {
        'symbol':symbol.upper(),
    }
    response = requests.get(url, params=params)
    order_data = response.json()
    order_df = pd.DataFrame([order_data])
    print(order_df)
    return order_df

get_latest_prices()
order_book()

