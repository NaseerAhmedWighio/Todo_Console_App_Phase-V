#!/bin/bash

echo "========================================="
echo "  Backend Service Build Script"
echo "========================================="

# Build backend image
echo "Building backend image..."
docker-compose build backend

if [ $? -eq 0 ]; then
    echo ""
    echo "Starting backend service..."
    docker-compose up -d backend
    
    echo ""
    echo "Waiting for backend to be healthy..."
    sleep 15
    
    echo ""
    echo "Backend service status:"
    docker-compose ps backend
    
    echo ""
    echo "✓ Backend is ready!"
    echo "  - API: http://localhost:7860"
    echo "  - API Docs: http://localhost:7860/docs"
else
    echo "✗ Backend build failed!"
    exit 1
fi
