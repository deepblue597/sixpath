# Docker Compose Setup for SixPath

This application supports both **SQLite** (for local development) and **PostgreSQL** (for Docker/production).

## 🗄️ SQLite vs PostgreSQL - Which to Use?

### Use **SQLite** when:

- ✅ Developing locally without Docker
- ✅ Quick prototyping or testing
- ✅ Single-user application
- ✅ No concurrent writes needed

### Use **PostgreSQL** when:

- ✅ Running in Docker containers
- ✅ Production deployment
- ✅ Multiple users accessing simultaneously
- ✅ Need better performance and scalability
- ✅ Planning to use network visualization features

**Recommendation**: Use **PostgreSQL with Docker** for this app since it's designed for network visualization which benefits from relational database features.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Start the services:**

   ```bash
   docker-compose up -d
   ```

2. **View logs:**

   ```bash
   docker-compose logs -f api
   ```

3. **Access the application:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

4. **Stop the services:**

   ```bash
   docker-compose down
   ```

5. **Stop and remove volumes (⚠️ deletes all data):**
   ```bash
   docker-compose down -v
   ```

## Services

### PostgreSQL Database (`db`)

- **Image**: postgres:16-alpine
- **Port**: 5432 (exposed to host)
- **Database**: sixpath
- **User**: sixpath_user
- **Password**: sixpath_password
- **Data**: Persisted in `postgres_data` volume

### FastAPI API (`api`)

- **Port**: 8000
- **Auto-reload**: Enabled in development
- **Access**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

## Environment Variables

The application uses environment variables for configuration:

### Database

- `DB_TYPE`: Database type (`sqlite` or `postgresql`) - default: `postgresql`
- `DB_HOST`: Database host - default: `localhost` (use `db` in Docker)
- `DB_PORT`: Database port - default: `5432`
- `DB_NAME`: Database name - default: `sixpath`
- `DB_USER`: Database user - default: `sixpath_user`
- `DB_PASSWORD`: Database password
- `SQLITE_DB_PATH`: Path to SQLite file (if using SQLite) - default: `./data/sixpath.db`

### JWT Authentication

- `JWT_SECRET_KEY`: Secret key for JWT tokens (⚠️ **REQUIRED - change in production!**)
- `JWT_ALGORITHM`: Algorithm - default: `HS256`
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration - default: `30`

### API

- `API_HOST`: Host to bind - default: `0.0.0.0`
- `API_PORT`: Port to bind - default: `8000`

## Development Workflow

### With Docker (PostgreSQL)

1. **Start services:**

   ```bash
   docker-compose up -d
   ```

2. **Make code changes** - they will auto-reload in the container

3. **View logs:**
   ```bash
   docker-compose logs -f api
   ```

### Without Docker (SQLite)

1. **Set up environment:**

   ```bash
   cp .env.example .env
   # Edit .env and set DB_TYPE=sqlite
   ```

2. **Install dependencies:**

   ```bash
   pip install -e .
   ```

3. **Run the API:**
   ```bash
   uvicorn api:app --reload
   ```

## Database Access

### Connect to PostgreSQL directly:

```bash
docker-compose exec db psql -U sixpath_user -d sixpath
```

### Run SQL commands:

```bash
docker-compose exec db psql -U sixpath_user -d sixpath -c "SELECT * FROM users;"
```

### Initialize/Reset Database:

```bash
# Connect to database
docker-compose exec db psql -U sixpath_user -d sixpath

# Run the SQL from database/sqlite.sql manually
# Note: You'll need to adjust the SQL for PostgreSQL syntax
```

## Troubleshooting

### Database connection issues:

```bash
docker-compose logs db
```

### API issues:

```bash
docker-compose logs api
```

### Rebuild containers after dependency changes:

```bash
docker-compose up -d --build
```

### Clear all data and restart:

```bash
docker-compose down -v
docker-compose up -d --build
```

### Check if services are healthy:

```bash
docker-compose ps
```

## Production Deployment

1. **Change JWT secret** in environment variables
2. **Use strong database password**
3. **Disable auto-reload** in docker-compose.yml (remove `--reload`)
4. **Use environment-specific .env files**
5. **Set up proper backups** for `postgres_data` volume
