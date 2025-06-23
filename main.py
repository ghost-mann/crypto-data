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

def recent_trades(symbol='BTCUSDT'):
    url = f'{BASE_URL}/api/v3/trades'
    params = {
        'symbol':symbol.upper()
    }
    response = requests.get(url,params=params)
    trades_data = response.json()
    trades_df = pd.DataFrame(trades_data)
    print(trades_df)
    return trades_df

def get_klines(symbol='BTCUSDT',interval='15m'):
    url = f'{BASE_URL}/api/v3/klines'
    params = {
        'symbol':symbol.upper(),
        'interval':interval
    }
    response = requests.get(url,params=params)
    kline_data = response.json()
    
    df_klines = pd.DataFrame(kline_data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])
    print(df_klines)
    return df_klines

# def ticker_stats():
    
    
# get_latest_prices()
# order_book()
# recent_trades()
# get_klines()

