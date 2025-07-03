

Python inserts data into → PostgreSQL 
PostgreSQL changes are detected by → Debezium 
Debezium sends changes to → Kafka 
Kafka passes changes to → Cassandra Sink Connector 
Connector writes them into → Cassandra database
