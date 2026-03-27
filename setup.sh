#!/bin/bash
set -e

echo "=== Sixpath Setup ==="

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "Docker is already installed: $(docker --version)"
else
    echo "Docker not found. Installing Docker..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Install Docker on Linux using the official convenience script
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        rm get-docker.sh
        sudo usermod -aG docker "$USER"
        echo "Docker installed. You may need to log out and back in for group changes to take effect."
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Please install Docker Desktop for Mac from: https://docs.docker.com/desktop/install/mac-install/"
        exit 1
    else
        echo "Unsupported OS. Please install Docker manually: https://docs.docker.com/get-docker/"
        exit 1
    fi
fi

# Verify Docker is running
if ! docker info &> /dev/null; then
    echo "Docker is installed but not running. Please start Docker and try again."
    exit 1
fi

# Check if docker compose is available
if docker compose version &> /dev/null; then
    echo "Docker Compose is available: $(docker compose version)"
else
    echo "Docker Compose not found. Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "Warning: No .env file found. The app requires environment variables to run."
    echo "Please create a .env file before proceeding."
    exit 1
fi

# Run the application
echo "Starting Sixpath application..."
docker compose up -d

echo ""
echo "=== Sixpath is running! ==="
echo "Frontend: http://localhost:3001"
echo "Backend:  http://localhost:8000"
echo "Database: localhost:5432"
