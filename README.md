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

### docker cassandra shell
docker exec -it cassandra cqlsh

