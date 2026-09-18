from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_postgis, create_tables
from routes_auth import router as auth_router
from routes_projects import router as projects_router
from routes_sites import router as sites_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown
    """
    # Startup: Initialize PostGIS and create tables
    print("🚀 Starting Darukaa.Earth API...")
    init_postgis()
    create_tables()
    print("✓ Database initialized successfully")
    yield
    # Shutdown
    print("👋 Shutting down Darukaa.Earth API...")


app = FastAPI(
    title="Darukaa.Earth API",
    version="1.0.0",
    description="API for managing restoration and conservation projects with PostGIS spatial data",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(sites_router)


@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Welcome to Darukaa.Earth API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth",
            "projects": "/projects",
            "sites": "/sites"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "database": "connected",
        "postgis": "enabled"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
