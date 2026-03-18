#!/bin/bash

echo "========================================="
echo "  Frontend Service Build Script"
echo "========================================="

# Build frontend image
echo "Building frontend image..."
docker-compose build frontend

if [ $? -eq 0 ]; then
    echo ""
    echo "Starting frontend service..."
    docker-compose up -d frontend
    
    echo ""
    echo "Waiting for frontend to be healthy..."
    sleep 15
    
    echo ""
    echo "Frontend service status:"
    docker-compose ps frontend
    
    echo ""
    echo "✓ Frontend is ready!"
    echo "  - Web UI: http://localhost:3000"
else
    echo "✗ Frontend build failed!"
    exit 1
fi
