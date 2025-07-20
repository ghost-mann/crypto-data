#!/bin/bash

# Get all connectors
echo "=== All Connectors ==="
curl -s -X GET http://localhost:8083/connectors | jq -r '.[]' | sort

echo -e "\n=== Connector Status Overview ==="
for connector in $(curl -s -X GET http://localhost:8083/connectors | jq -r '.[]'); do
    status=$(curl -s -X GET "http://localhost:8083/connectors/$connector/status" | jq -r '.connector.state')
    echo "$connector: $status"
done

echo -e "\n=== Detailed Status for Each Connector ==="
for connector in $(curl -s -X GET http://localhost:8083/connectors | jq -r '.[]'); do
    echo "--- $connector ---"
    curl -s -X GET "http://localhost:8083/connectors/$connector/status" | jq '.'
    echo
done

echo -e "\n=== Configuration for Cassandra Connectors ==="
for connector in $(curl -s -X GET http://localhost:8083/connectors | jq -r '.[]' | grep cassandra); do
    echo "--- $connector Configuration ---"
    curl -s -X GET "http://localhost:8083/connectors/$connector/config" | jq '.'
    echo
done

echo -e "\n=== Recent Tasks with Errors ==="
for connector in $(curl -s -X GET http://localhost:8083/connectors | jq -r '.[]'); do
    status_response=$(curl -s -X GET "http://localhost:8083/connectors/$connector/status")
    task_state=$(echo "$status_response" | jq -r '.tasks[0].state // "N/A"')
    if [ "$task_state" = "FAILED" ]; then
        echo "--- $connector (FAILED) ---"
        echo "$status_response" | jq '.tasks[0].trace'
        echo
    fi
done