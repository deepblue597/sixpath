# SixPaths - Full Stack Setup Guide

This guide explains how to run the complete SixPaths application with both the FastAPI backend and Streamlit frontend.

## Architecture

```
┌─────────────────────────────────────┐
│   Streamlit Frontend (Port 8501)    │
│   - Login & Authentication          │
│   - Network Visualization           │
│   - Connection Management           │
│   - Referral Tracking               │
└──────────────┬──────────────────────┘
               │ HTTP/REST API
               ↓
┌─────────────────────────────────────┐
│   FastAPI Backend (Port 8000)       │
│   - JWT Authentication              │
│   - User Management                 │
│   - Connection CRUD                 │
│   - Referral CRUD                   │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│   PostgreSQL Database               │
│   - Users Table                     │
│   - Connections Table               │
│   - Referrals Table                 │
└─────────────────────────────────────┘
```

## Prerequisites

- Python 3.10+
- PostgreSQL database (or Docker for containerized DB)
- uv (Python package manager) or pip

## Installation

### 1. Install Dependencies

```bash
# Install all dependencies
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Database Setup

#### Option A: Using Docker Compose

```bash
# Start PostgreSQL database
docker compose up -d

# Check if database is running
docker compose ps
```

#### Option B: Local PostgreSQL

1. Install PostgreSQL locally
2. Create a database:

```sql
CREATE DATABASE sixpath;
```

3. Run the schema:

```bash
psql -U postgres -d sixpath -f database/sqlite.sql
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sixpath
DB_USER=postgres
DB_PASSWORD=your_password

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_URL=http://localhost:8000
```

## Running the Application

### Step 1: Start the Backend API

```bash
# Using uv
uv run api.py

# Or using uvicorn directly
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Step 2: Start the Streamlit Frontend

In a **new terminal**:

```bash
# Using uv
uv run streamlit run streamlit_app.py

# Or using streamlit directly
streamlit run streamlit_app.py
```

The frontend will be available at:

- Web App: http://localhost:8501

## Creating Your First User

### Option 1: Using the API

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "company": "TechCorp",
    "sector": "Technology",
    "is_me": true
  }'
```

### Option 2: Using API Docs

1. Go to http://localhost:8000/docs
2. Find the `POST /users/` endpoint
3. Click "Try it out"
4. Fill in the user data
5. Click "Execute"

### Option 3: Using Python Script

Create a file `create_user.py`:

```python
import requests

response = requests.post("http://localhost:8000/users/", json={
    "username": "johndoe",
    "password": "securepassword",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "company": "TechCorp",
    "sector": "Technology",
    "is_me": True
})

print(response.json())
```

Run it:

```bash
python create_user.py
```

## Using the Application

### 1. Login

- Open http://localhost:8501
- Enter your email and password
- Click "Login"

### 2. Dashboard

- View your network visualization
- Filter by sector or company
- Click nodes to edit connections
- Use sidebar controls

### 3. Manage Connections

- Click "Add Connection" to create new connections
- Click on network nodes to edit existing connections
- Update relationship details, strength, notes

### 4. Track Referrals

- Navigate to "Referrals" page
- View all your job referrals
- Filter and search referrals
- Export to CSV

### 5. Edit Profile

- Navigate to "Profile" page
- Update your information
- Changes sync to backend

## API Endpoints

### Authentication

- `POST /auth/login` - Login and get JWT token

### Users

- `GET /users/me` - Get current user info
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user
- `POST /users/` - Create new user

### Connections

- `GET /connections/user/{user_id}` - Get user's connections
- `GET /connections/{connection_id}` - Get connection by ID
- `POST /connections/` - Create connection
- `PUT /connections/{connection_id}` - Update connection
- `DELETE /connections/{connection_id}` - Delete connection

### Referrals

- `GET /referrals/me` - Get current user's referrals
- `GET /referrals/{referral_id}` - Get referral by ID
- `POST /referrals/` - Create referral
- `PUT /referrals/{referral_id}` - Update referral
- `DELETE /referrals/{referral_id}` - Delete referral

## Development

### Running Tests

```bash
# Run backend tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy .
```

## Troubleshooting

### Backend won't start

- Check database connection in `.env`
- Verify PostgreSQL is running: `docker compose ps`
- Check logs: `docker compose logs`

### Frontend can't connect to backend

- Ensure backend is running on port 8000
- Check API_URL in `.env` or Streamlit secrets
- Verify no firewall blocking

### Login fails

- Ensure user exists in database
- Check credentials are correct
- Verify JWT secret is set in `.env`

### Database connection errors

- Check PostgreSQL is running
- Verify database credentials in `.env`
- Ensure database exists

## Production Deployment

### Environment Variables

Set these for production:

```env
# Strong secret key
SECRET_KEY=<generate-strong-random-key>

# Production database
DB_HOST=your-production-db-host
DB_NAME=sixpath_prod

# Disable debug mode
DEBUG=False
```

### Security Considerations

1. **JWT Secret**: Use a strong, random secret key
2. **HTTPS**: Deploy behind HTTPS reverse proxy
3. **CORS**: Configure CORS properly in `api.py`
4. **Database**: Use secure database credentials
5. **Environment**: Never commit `.env` file

### Deployment Options

#### Option 1: Docker

```bash
# Build and run with docker compose
docker compose up --build
```

#### Option 2: Cloud Platform

- Backend: Deploy to AWS ECS, Azure App Service, or Google Cloud Run
- Frontend: Deploy to Streamlit Cloud, AWS, or Azure
- Database: Use managed PostgreSQL (AWS RDS, Azure Database, etc.)

## API Authentication Flow

1. User enters credentials in Streamlit
2. Frontend sends credentials to `/auth/login`
3. Backend validates and returns JWT token
4. Frontend stores token in session state
5. All subsequent API calls include token in Authorization header
6. Backend validates token on each request

## Project Structure

```
sixpath/
├── api.py                 # FastAPI application entry point
├── streamlit_app.py       # Streamlit frontend entry point
├── pages/                 # Streamlit pages
│   ├── 01_Login.py
│   ├── 02_Dashboard.py
│   ├── 03_Referrals.py
│   ├── 04_Edit_Profile.py
│   └── 05_Edit_Connection.py
├── routers/               # API route handlers
│   ├── auth.py
│   ├── users.py
│   ├── connections.py
│   └── referrals.py
├── services/              # Business logic
│   ├── userService.py
│   ├── connectionService.py
│   └── referralService.py
├── dao/                   # Database access objects
│   ├── userDAO.py
│   ├── connectionDAO.py
│   └── referralDAO.py
├── models/                # Pydantic models
│   ├── input_models.py
│   ├── response_models.py
│   └── database_models.py
├── utils/                 # Utilities
│   ├── api_client.py      # Frontend API client
│   ├── data_transformer.py # Data transformation
│   ├── styling.py         # Frontend styling
│   ├── mock_data.py       # Sample data (deprecated)
│   ├── config.py          # Configuration
│   ├── dependencies.py    # DI
│   └── oath2.py           # JWT handling
└── database/              # Database scripts
    └── sqlite.sql
```

## Support

For issues or questions:

1. Check this README
2. Review API docs at http://localhost:8000/docs
3. Check application logs
4. Review error messages in Streamlit

## License

This project is for demonstration purposes.

---

**SixPaths** © 2026 | Professional Networking Made Visual
