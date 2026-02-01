# Docker Setup with UV

This project uses Docker Compose to run the full stack application with separate containers for the database, backend API, and frontend.

## Architecture

- **Database (db)**: PostgreSQL 16
- **Backend (backend)**: FastAPI application running on port 8000
- **Frontend (frontend)**: Streamlit application running on port 8501

All services use `uv` for Python package management.

## Prerequisites

- Docker
- Docker Compose
- (Optional) Make sure `.env` file has your `JWT_SECRET_KEY` set

## Quick Start

### Build and Start All Services

```bash
docker-compose up --build
```

### Start Services (without rebuild)

```bash
docker-compose up
```

### Run in Detached Mode

```bash
docker-compose up -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Stop Services

```bash
docker-compose down
```

### Stop and Remove Volumes (includes database data)

```bash
docker-compose down -v
```

## Accessing the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

## Development Workflow

### Rebuild a Specific Service

```bash
docker-compose build backend
docker-compose build frontend
```

### Restart a Specific Service

```bash
docker-compose restart backend
docker-compose restart frontend
```

### Execute Commands in a Running Container

```bash
# Backend container
docker-compose exec backend bash

# Frontend container
docker-compose exec frontend bash

# Database container
docker-compose exec db psql -U sixpath_user -d sixpath
```

### View Service Status

```bash
docker-compose ps
```

## UV Package Management

Both Dockerfiles use `uv` for dependency management:

- Dependencies are defined in workspace `pyproject.toml` and app-specific `pyproject.toml` files
- The `uv sync --frozen --no-dev` command installs dependencies in production mode
- The workspace structure is preserved with the shared `packages/models` module

## Environment Variables

Key environment variables (set in docker-compose.yml):

### Backend

- `DB_TYPE`: Database type (postgresql)
- `DB_HOST`: Database hostname (db)
- `DB_PORT`: Database port (5432)
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `JWT_ALGORITHM`: JWT algorithm (HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### Frontend

- `BACKEND_URL`: Backend API URL (http://backend:8000)
- `STREAMLIT_SERVER_PORT`: Streamlit port (8501)
- `STREAMLIT_SERVER_ADDRESS`: Streamlit address (0.0.0.0)

## Troubleshooting

### Database Connection Issues

If the backend can't connect to the database:

1. Check if the database is healthy:

   ```bash
   docker-compose ps
   ```

2. View database logs:

   ```bash
   docker-compose logs db
   ```

3. The backend waits for the database health check to pass before starting

### Port Conflicts

If ports 8000, 8501, or 5432 are already in use:

1. Change the ports in `docker-compose.yml`:
   ```yaml
   ports:
     - "NEW_PORT:8000" # for backend
     - "NEW_PORT:8501" # for frontend
     - "NEW_PORT:5432" # for database
   ```

### Rebuild from Scratch

If you encounter persistent issues:

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## File Structure

```
/mnt/disk2/homeProjects/sixpath/
├── docker-compose.yml           # Orchestrates all services
├── pyproject.toml              # Workspace root dependencies
├── apps/
│   ├── backend/
│   │   ├── Dockerfile          # Backend container definition
│   │   ├── pyproject.toml      # Backend dependencies
│   │   └── api.py              # Backend entry point
│   └── frontend/
│       ├── Dockerfile          # Frontend container definition
│       ├── pyproject.toml      # Frontend dependencies
│       └── app.py              # Frontend entry point
└── packages/
    └── models/                 # Shared models package
```

## Production Considerations

For production deployment:

1. **Change the JWT secret**: Set a strong `JWT_SECRET_KEY` via environment variables
2. **Use environment-specific configs**: Create separate docker-compose files for dev/staging/prod
3. **Enable HTTPS**: Add a reverse proxy (nginx/traefik) in front of the services
4. **Volume management**: Use named volumes or bind mounts for persistent data
5. **Resource limits**: Add memory and CPU limits to service definitions
6. **Remove development features**:
   - Remove `--reload` flag from uvicorn
   - Enable production mode for Streamlit
7. **Security**: Don't expose database port to host in production
