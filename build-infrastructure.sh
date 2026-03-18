#!/bin/bash

echo "========================================="
echo "  Infrastructure Services Build Script"
echo "========================================="

# Pull and start infrastructure services (pre-built images)
echo "[1/3] Pulling Zookeeper..."
docker-compose pull zookeeper

echo "[2/3] Pulling Kafka..."
docker-compose pull kafka

echo "[3/3] Pulling Redis..."
docker-compose pull redis

echo ""
echo "Starting infrastructure services..."
docker-compose up -d zookeeper kafka redis

echo ""
echo "Waiting for services to be healthy..."
sleep 10

echo ""
echo "Infrastructure services status:"
docker-compose ps zookeeper kafka redis

echo ""
echo "✓ Infrastructure services are ready!"
echo "  - Zookeeper: localhost:2181"
echo "  - Kafka: localhost:9092"
echo "  - Redis: localhost:6379"
