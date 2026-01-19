"""
FastAPI backend for user management system.
Provides CRUD operations for users stored in PostgreSQL.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, status , Request
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from config import get_settings
from services.userService import UserService
from utils.dependencies import set_user_service,  get_user_service
from routers import users , auth
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Replaces the deprecated @app.on_event decorators.
    """
    # Startup: Initialize factories and services
    # Load settings from environment
    settings = get_settings()
    DATABASE_URL = settings.database_url
    
    
    print(f"🔧 Connecting to database: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    
    # Initialize database engine
    postgres_engine = create_engine(DATABASE_URL)
    


    # Initialize services
    user_service = UserService(engine=postgres_engine)

    
    # Set services in dependencies module for injection
    set_user_service(user_service)
    
    print("✅ DAO factories and services initialized")
    
    yield  # Application runs here
    
    # Shutdown: Cleanup resources (if needed)
    print("🛑 Shutting down application...")
    # Add cleanup code here if needed (e.g., closing connections)


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="User Management API",
    description="REST API for managing users with PostgreSQL backend",
    version="1.0.0",
    lifespan=lifespan
)

# Import routers after app is created to avoid circular imports


# Include all routers
app.include_router(auth.router)       # /auth/* endpoints
app.include_router(users.router)      # /users/* endpoints



# Middleware to log request processing time
@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time
    print(f"{request.method} {request.url.path} took {duration:.4f} seconds")
    return response

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "User Management API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "auth": "/auth",
            "users": "/users"
        }
    }


@app.get("/health")
async def health_check(user_service: UserService = Depends(get_user_service)):
    """Health check endpoint to verify database connectivity"""
    try:
        users = user_service.get_users()
        return {
            "status": "healthy",
            "database": "connected",
            "users_count": len(users)
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        app, 
        host=settings.api_host, 
        port=settings.api_port,
        log_level="info"
    )
