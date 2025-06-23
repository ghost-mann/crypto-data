import requests
import pandas as pd
import time

BASE_URL = "https://api.binance.com"

def get_latest_prices(symbol='BTCUSDT'):
    url = f'{BASE_URL}/api/v3/ticker/price'
    params = {
        'symbol':symbol.upper()
    }
    response = requests.get(url,params=params)
    data = response.json()
    df_prices = pd.DataFrame([data])
    print(df_prices)
    return df_prices
    
def order_book(symbol='BTCUSDT',limit=5):
    url = f'{BASE_URL}/api/v3/depth'
    params = {
        'symbol':symbol.upper(),
    }
    response = requests.get(url, params=params)
    order_data = response.json()
    
    bids_df = pd.DataFrame(order_data['bids'], columns=['price','quantity'])
    asks_df = pd.DataFrame(order_data['asks'], columns=['price','quantity'])
    print('bids')
    print(bids_df)
    print('asks')
    print(asks_df)
    
    return bids_df,asks_df

get_latest_prices()
order_book()

