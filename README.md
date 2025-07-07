Python inserts data into → PostgreSQL 
PostgreSQL changes are detected by → Debezium 
Debezium sends changes to → Kafka 
Kafka passes changes to → Cassandra Sink Connector 
Connector writes them into → Cassandra database


- The python script requests data using Binance Api endpoints in json format which is then transformed and stored into a DataFrame.

- Change tracking is enabled in PostgreSQL so that every insert/delete/update is logged.


*** DOCKER COMMANDS ***
 docker exec -it kafka bash - start kafka cli 


