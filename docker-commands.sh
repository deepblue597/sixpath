#!/bin/bash
# Quick commands for Docker operations

# Build and start all services
echo "To build and start all services:"
echo "  docker-compose up --build"
echo ""

# Start in background
echo "To start in background (detached mode):"
echo "  docker-compose up -d"
echo ""

# Stop services
echo "To stop all services:"
echo "  docker-compose down"
echo ""

# View logs
echo "To view logs:"
echo "  docker-compose logs -f              # All services"
echo "  docker-compose logs -f backend      # Backend only"
echo "  docker-compose logs -f frontend     # Frontend only"
echo "  docker-compose logs -f db           # Database only"
echo ""

# Rebuild specific service
echo "To rebuild a specific service:"
echo "  docker-compose build backend"
echo "  docker-compose build frontend"
echo ""

# Access containers
echo "To access a container:"
echo "  docker-compose exec backend bash"
echo "  docker-compose exec frontend bash"
echo "  docker-compose exec db psql -U sixpath_user -d sixpath"
echo ""

# Clean restart
echo "To perform a clean restart (removes volumes):"
echo "  docker-compose down -v"
echo "  docker-compose build --no-cache"
echo "  docker-compose up"
