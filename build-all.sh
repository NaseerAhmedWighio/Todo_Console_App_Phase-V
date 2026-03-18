#!/bin/bash

echo "========================================="
echo "  Full Stack Build & Start Script"
echo "========================================="

echo ""
echo "=== Step 1: Infrastructure Services ==="
docker-compose pull zookeeper kafka redis
docker-compose up -d zookeeper kafka redis

echo ""
echo "Waiting for infrastructure to be ready..."
sleep 15

echo ""
echo "=== Step 2: Build Backend ==="
docker-compose build backend

echo ""
echo "=== Step 3: Build Frontend ==="
docker-compose build frontend

echo ""
echo "=== Step 4: Start All Services ==="
docker-compose up -d backend frontend

echo ""
echo "Waiting for all services to be healthy..."
sleep 20

echo ""
echo "========================================="
echo "  All Services Status"
echo "========================================="
docker-compose ps

echo ""
echo "========================================="
echo "  Service Endpoints"
echo "========================================="
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:7860"
echo "  API Docs:  http://localhost:7860/docs"
echo "  Kafka:     localhost:9092"
echo "  Redis:     localhost:6379"
echo "  Zookeeper: localhost:2181"
echo "========================================="
echo ""
echo "✓ Full stack is ready!"
