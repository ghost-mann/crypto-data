import requests
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from datetime import datetime, timezone
from kafka import KafkaProducer
import json
from decimal import Decimal

load_dotenv()

db_user = os.getenv('AIVEN_USERNAME')
db_password = os.getenv('AIVEN_PASSWORD')
db_host = os.getenv('AIVEN_HOST')
db_name = os.getenv('AIVEN_DBNAME')
db_port = os.getenv('AIVEN_PORT')

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Try both bootstrap servers - adjust based on your setup
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092', 'localhost:29092'],  # Try both
    value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
    key_serializer=lambda x: x.encode('utf-8') if x else None,
    acks='all',  # Wait for all replicas to acknowledge
    retries=3,
    batch_size=16384,
    linger_ms=10
)

BASE_URL = "https://api.binance.com"
TOP_PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
INTERVAL = '15m'

def clean_record_for_cassandra(record):
    """Clean record to ensure compatibility with Cassandra"""
    cleaned = {}
    for key, value in record.items():
        if isinstance(value, pd.Timestamp):
            cleaned[key] = value.isoformat()
        elif pd.isna(value):
            cleaned[key] = None
        elif isinstance(value, (int, float)):
            # Convert to string for decimal fields to avoid precision issues
            cleaned[key] = str(value)
        elif isinstance(value, bool):
            cleaned[key] = value
        else:
            cleaned[key] = str(value)
    return cleaned

def save_to_postgres_and_kafka(df, table_name, topic_name):
    try:
        # Save to PostgreSQL
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f'Saved {len(df)} rows to PostgreSQL table: {table_name}')
        
        # Send to Kafka
        success_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            record = clean_record_for_cassandra(row.to_dict())
            
            try:
                future = producer.send(
                    topic_name, 
                    value=record,
                    key=record.get('symbol', 'unknown')
                )
                # Wait for the send to complete
                result = future.get(timeout=10)
                success_count += 1
                print(f'Sent record to {topic_name}: {record.get("symbol", "unknown")}')
            except Exception as e:
                error_count += 1
                print(f'Error sending record to {topic_name}: {e}')
        
        producer.flush()
        print(f'Kafka summary - Topic: {topic_name}, Success: {success_count}, Errors: {error_count}')
        
    except Exception as e:
        print(f'Error saving {table_name}: {e}')

def get_latest_prices(symbol):
    url = f'{BASE_URL}/api/v3/ticker/price'
    response = requests.get(url, params={'symbol': symbol})
    data = response.json()
    df = pd.DataFrame([data])
    df['fetched_at'] = datetime.now(timezone.utc)
    df['symbol'] = symbol
    return df

def order_book(symbol, limit=20):
    url = f'{BASE_URL}/api/v3/depth'
    response = requests.get(url, params={'symbol': symbol, 'limit': limit})
    order_data = response.json()
    bids_df = pd.DataFrame(order_data['bids'], columns=['price', 'quantity'])
    asks_df = pd.DataFrame(order_data['asks'], columns=['price', 'quantity'])
    fetched_at = datetime.now(timezone.utc)
    bids_df['fetched_at'] = fetched_at
    asks_df['fetched_at'] = fetched_at
    bids_df['symbol'] = symbol
    asks_df['symbol'] = symbol
    return bids_df, asks_df

def recent_trades(symbol, limit=20):
    url = f'{BASE_URL}/api/v3/trades'
    response = requests.get(url, params={'symbol': symbol, 'limit': limit})
    trades_data = response.json()
    df = pd.DataFrame(trades_data)
    df['symbol'] = symbol
    df['fetched_at'] = datetime.now(timezone.utc)
    return df

def get_klines(symbol, interval='15m'):
    url = f'{BASE_URL}/api/v3/klines'
    response = requests.get(url, params={'symbol': symbol, 'interval': interval})
    kline_data = response.json()
    df = pd.DataFrame(kline_data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])
    df['fetched_at'] = datetime.now(timezone.utc)
    df['symbol'] = symbol
    return df

def ticker_stats(symbol):
    url = f'{BASE_URL}/api/v3/ticker/24hr'
    response = requests.get(url, params={'symbol': symbol})
    ticker_data = response.json()
    df = pd.DataFrame([ticker_data])
    df['fetched_at'] = datetime.now(timezone.utc)
    df['symbol'] = symbol
    return df

# Test connectivity first
print("Testing Kafka connectivity...")
try:
    metadata = producer.bootstrap_connected()
    print(f"Kafka connection successful: {metadata}")
except Exception as e:
    print(f"Kafka connection failed: {e}")

# Main loop
try:
    for symbol in TOP_PAIRS:
        print(f'\n=== Collecting data for {symbol} ===')

        price_df = get_latest_prices(symbol)
        save_to_postgres_and_kafka(price_df, "latest_prices", "binance.public.latest_prices")

        trades_df = recent_trades(symbol)
        save_to_postgres_and_kafka(trades_df, "recent_trades", "binance.public.recent_trades")

        klines_df = get_klines(symbol)
        save_to_postgres_and_kafka(klines_df, "klines_15m", "binance.public.klines_15m")

        ticker_df = ticker_stats(symbol)
        save_to_postgres_and_kafka(ticker_df, "stats_24h", "binance.public.stats_24h")

        bids_df, asks_df = order_book(symbol)
        save_to_postgres_and_kafka(bids_df, "orderbook_bids", "binance.public.orderbook_bids")
        save_to_postgres_and_kafka(asks_df, "orderbook_asks", "binance.public.orderbook_asks")

        print(f'Completed data collection for {symbol}')

finally:
    producer.close()
    print("Kafka producer closed!")