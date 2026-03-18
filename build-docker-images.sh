#!/bin/bash

# Docker Image Build Script for Todo App Phase-V
# This script builds both backend and frontend Docker images

set -e  # Exit on error

echo "=========================================="
echo "  Todo App Phase-V - Docker Image Build  "
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to print colored messages
print_message() {
    echo -e "${BLUE}>>> $1${NC}"
}

print_success() {
    echo -e "${GREEN}>>> $1${NC}"
}

print_error() {
    echo -e "${RED}>>> ERROR: $1${NC}"
}

# Check if Docker is running
print_message "Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi
print_success "Docker is running"
echo ""

# Build backend image
print_message "Building backend image (todo-backend:latest)..."
cd "$SCRIPT_DIR/backend"
if docker build -t todo-backend:latest .; then
    print_success "Backend image built successfully!"
else
    print_error "Failed to build backend image"
    exit 1
fi
echo ""

# Build frontend image
print_message "Building frontend image (todo-frontend:latest)..."
cd "$SCRIPT_DIR/frontend"
if docker build -t todo-frontend:latest .; then
    print_success "Frontend image built successfully!"
else
    print_error "Failed to build frontend image"
    exit 1
fi
echo ""

# Show image information
print_message "Build Summary:"
echo ""
echo "Backend Image:"
docker images todo-backend:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"
echo ""
echo "Frontend Image:"
docker images todo-frontend:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"
echo ""

print_success "All images built successfully!"
echo ""
echo "Next steps:"
echo "  1. Test locally: docker-compose up -d"
echo "  2. Load into Minikube: minikube image load todo-backend:latest todo-frontend:latest"
echo "  3. Push to registry: docker push your-registry/todo-backend:latest"
echo ""
