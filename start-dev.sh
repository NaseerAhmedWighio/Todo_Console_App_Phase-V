#!/bin/bash
# Docker Development Startup Script
# Starts infrastructure (Kafka, Redis) in Docker, runs backend locally

echo "===================================="
echo "Todo App Phase V - Development Mode"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found!"
    echo "Copy .env.example to .env and configure your environment variables."
    echo ""
fi

# Check if backend/.env exists
if [ ! -f "backend/.env" ]; then
    echo "[WARNING] backend/.env file not found!"
    echo "Copy backend/.env.example to backend/.env and configure your environment variables."
    echo ""
fi

# Start Docker infrastructure
echo "[1/3] Starting Docker infrastructure (Kafka, Redis)..."
docker-compose -f docker-compose.dev.yml up -d kafka zookeeper redis

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to start Docker services!"
    exit 1
fi

echo "[2/3] Waiting for services to be ready..."
sleep 10

echo "[3/3] Starting backend locally..."
echo ""
echo "===================================="
echo "Services Status:"
echo "===================================="
echo "  Frontend:  Will be available at http://localhost:3000 (after you start it)"
echo "  Backend:   Starting at http://localhost:7860"
echo "  Kafka:     localhost:9092"
echo "  Redis:     localhost:6379"
echo ""
echo "===================================="
echo "Next Steps:"
echo "===================================="
echo "  1. Backend is starting now..."
echo "  2. In another terminal, run: docker-compose -f docker-compose.dev-frontend.yml up"
echo "     OR run: cd frontend && npm run dev"
echo ""
echo "To stop Docker services: docker-compose -f docker-compose.dev.yml down"
echo ""

# Start backend locally
cd backend
python -m uvicorn main:app --reload --port 7860
