# REAL TIME CRYPTOCURRENCY DATA PIPELINE

## Workflow

binance api --> binance collector --> debezium/postgres --> debezium/connect --> kafka(zookeeper) --> cassandra --> grafana

Python inserts data into → PostgreSQL 
PostgreSQL changes are detected by → Debezium 
Debezium sends changes to → Kafka 
Kafka passes changes to → Cassandra Sink Connector 
Connector writes them into → Cassandra database

- The python script requests data using Binance Api endpoints in json format which is then transformed and stored into a DataFrame.

- Change tracking is enabled in PostgreSQL so that every insert/delete/update is logged.

## Environment setup

### binance-collector

#### Setup environment variables

    cp .env.dist .env

#### Run on host

    python main.py

#### Run inside docker

##### Building docker image using dockerfile

    docker build -t binance-collector .

##### Run it

    docker run --network="host" --env-file .env binance-collector

    docker run --rm --network="host" --env-file .env --name binance-collector binance-collector

## FAQ

### Running kafka shell in docker

    docker exec -it kafka bash - start kafka cli

### docker cassandra shell
docker exec -it cassandra cqlsh

### docker postgres shell
docker exec -it postgres bash 

psql -U postgres -d postgres

### checking connector status
curl -s http://localhost:8083/connectors | jq  

### registering connector
$ curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  --data @postgres-debezium-source.json

### check status 
curl -s http://localhost:8083/connectors/cassandra-sink-connector/status | jq

### Delete the connector
curl -X DELETE http://localhost:8083/connectors/cassandra-sink-connector

### Recreate it with your configuration
curl -X PUT http://localhost:8083/connectors/cassandra-sink-connector/config \
  -H "Content-Type: application/json" \
  --data @cassandra-sink.json


## SQL
### Check if keyspace exists
DESCRIBE KEYSPACES;

### Use the keyspace (replace 'binance' with your actual keyspace name)
USE binance;

### List all tables
DESCRIBE TABLES;

### Check data in each table
SELECT * FROM latest_prices LIMIT 10;
SELECT * FROM recent_trades LIMIT 10;
SELECT * FROM klines_15m LIMIT 10;
SELECT * FROM stats_24h LIMIT 10;
SELECT * FROM orderbook_bids LIMIT 10;
SELECT * FROM orderbook_asks LIMIT 10;

### Check row counts
SELECT COUNT(*) FROM latest_prices;
SELECT COUNT(*) FROM recent_trades;

curl http://localhost:8083/connectors/cassandra-sink-connector/status


kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic binance.public.latest_prices --from-beginning --max-messages 5


kafka-topics --create --topic binance.recent_trades --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

kafka-topics --create --topic binance.klines_15m --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

kafka-topics --create --topic binance.stats_24h --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

kafka-topics --create --topic binance.orderbook_bids --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

kafka-topics --create --topic binance.orderbook_asks --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1



