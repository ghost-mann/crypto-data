import requests
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from datetime import datetime, timezone
from kafka import KafkaProducer
import json

load_dotenv()

db_user = os.getenv('AIVEN_USERNAME')
db_password = os.getenv('AIVEN_PASSWORD')
db_host = os.getenv('AIVEN_HOST')
db_name = os.getenv('AIVEN_DBNAME')
db_port = os.getenv('AIVEN_PORT')

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    key_serializer=lambda x: x.encode('utf-8') if x else None
)


BASE_URL = "https://api.binance.com"
TOP_PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
INTERVAL = '15m'

def save_to_postgres_and_kafka(df, table_name, topic_name):
    try:
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f'Saved to PostgreSQL table: {table_name}')
        
        # iterates over each row of df
        for _, row in df.iterrows():
            record = row.to_dict()
            # Convert Timestamp objects to strings
            for key, value in record.items():
                if isinstance(value, pd.Timestamp):
                    record[key] = value.isoformat()
                elif pd.isna(value):
                    record[key] = None
            
            producer.send(
                topic_name, 
                value=record,
                key=record.get('symbol', 'unknown')
            )
        
        producer.flush()
        print(f'Sent to Kafka topic: {topic_name}')
        
    
    except Exception as e:
        print(f'Error saving {table_name}: {e}')


def get_latest_prices(symbol):
    url = f'{BASE_URL}/api/v3/ticker/price'
    response = requests.get(url,params={'symbol':symbol})
    data = response.json()
    df = pd.DataFrame([data])
    df['fetched_at'] = datetime.now(timezone.utc)
    df['symbol'] = symbol
    print(df)
    return df
    
def order_book(symbol,limit=20):
    url = f'{BASE_URL}/api/v3/depth'
    response = requests.get(url, params={'symbol':symbol, 'limit':limit})
    order_data = response.json()
    bids_df = pd.DataFrame(order_data['bids'], columns=['price','quantity'])
    asks_df = pd.DataFrame(order_data['asks'], columns=['price','quantity'])
    bids_df['fetched_at'] = datetime.now(timezone.utc)
    asks_df['fetched_at'] = datetime.now(timezone.utc)
    bids_df['symbol'] = symbol
    asks_df['symbol'] = symbol
    print(bids_df)
    print(asks_df)
    return bids_df,asks_df

def recent_trades(symbol, limit=20):
    url = f'{BASE_URL}/api/v3/trades'
    response = requests.get(url,params={'symbol':symbol, 'limit':limit})
    trades_data = response.json()
    df = pd.DataFrame(trades_data)
    df['symbol'] = symbol
    df['fetched_at'] = datetime.now(timezone.utc)
    print(df.describe())
    return df

def get_klines(symbol,interval='15m'):
    url = f'{BASE_URL}/api/v3/klines'
    response = requests.get(url,params={'symbol':symbol, 'interval':interval})
    kline_data = response.json()
    
    df = pd.DataFrame(kline_data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])
    df['fetched_at'] = datetime.now(timezone.utc)
    df['symbol'] = symbol
    print(df)
    return df

def ticker_stats(symbol):
    url = f'{BASE_URL}/api/v3/ticker/24hr'
    response = requests.get(url,params={'symbol':symbol})
    ticker_data = response.json()
    df = pd.DataFrame([ticker_data])
    df['fetched_at'] = datetime.now(timezone.utc)
    df['symbol'] = symbol
    print(df)
    return df
  
# main loop
try:
    for symbol in TOP_PAIRS:
        print(f'Collecting data for {symbol}')
        
        price_df = get_latest_prices(symbol)
        save_to_postgres_and_kafka(price_df,"latest_prices","latest_price")
        
        trades_df = recent_trades(symbol)
        save_to_postgres_and_kafka(trades_df, "recent_trades","recent_trades")
        
        klines_df = get_klines(symbol)
        save_to_postgres_and_kafka(klines_df, "klines_15m","klines_15m")
        
        ticker_df = ticker_stats(symbol)
        save_to_postgres_and_kafka(ticker_df, "stats_24h","stats_24h")
        
        bids_df, asks_df = order_book(symbol)
        save_to_postgres_and_kafka(bids_df, "orderbook_bids","orderbook_bids")
        save_to_postgres_and_kafka(asks_df, "orderbook_asks","orderbook_asks")

finally:
    producer.close()
    print("Kafka closed!")
        
   
