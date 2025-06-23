import requests
import pandas as pd
import time

BASE_URL = "https://api.binance.com"

def get_latest_prices():
    url = f'{BASE_URL}/api/v3/ticker/price'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)
    print(df)
    
def order_book():
    