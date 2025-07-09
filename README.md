# REAL TIME CRYPTOCURRENCY DATA PIPELINE

## workflow
binance api --> debezium/postgres --> debezium/connect --> kafka(zookeeper) --> cassandra


Python inserts data into → PostgreSQL 
PostgreSQL changes are detected by → Debezium 
Debezium sends changes to → Kafka 
Kafka passes changes to → Cassandra Sink Connector 
Connector writes them into → Cassandra database


- The python script requests data using Binance Api endpoints in json format which is then transformed and stored into a DataFrame.

- Change tracking is enabled in PostgreSQL so that every insert/delete/update is logged.


## DOCKER COMMANDS 

### running kafka shell in docker
docker exec -it kafka bash - start kafka cli

### building docker image using dockerfile
docker build -t binance-collector .

### running docker image
docker run --network="host" --env-file .env binance-collector

docker run --rm --network="host" --env-file .env --name binance-collector binance-collector

### docker cassandra shell
docker exec -it cassandra cqlsh

### docker postgres shell
docker exec -it postgres bash 

psql -U postgres -d postgres

### checking connector status
curl -s http://localhost:8083/connectors | jq  

### registering connector 
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