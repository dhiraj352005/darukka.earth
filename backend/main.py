from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import json

from database import init_postgis, create_tables
from routes_auth import router as auth_router
from routes_projects import router as projects_router
from routes_sites import router as sites_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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


# Custom middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests for debugging"""
    logger.info(f"🔍 INCOMING REQUEST:")
    logger.info(f"  Method: {request.method}")
    logger.info(f"  URL: {request.url}")
    logger.info(f"  Origin: {request.headers.get('origin', 'No origin')}")
    logger.info(f"  Headers: {dict(request.headers)}")
    
    # Process the request
    response = await call_next(request)
    
    # Log the response
    logger.info(f"📤 RESPONSE:")
    logger.info(f"  Status: {response.status_code}")
    logger.info(f"  CORS Headers: {[(k, v) for k, v in response.headers.items() if 'access-control' in k.lower()]}")
    
    return response


# Configure CORS - Allow all origins for public access
# IMPORTANT: CORS middleware must be added BEFORE including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins - open access
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers to client
)

# Include routers (no /api prefix - handled by vercel routing)
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


@app.options("/test-cors")
async def test_cors():
    """
    Test endpoint to verify CORS is working
    """
    logger.info("🧪 CORS test endpoint called")
    return {"message": "CORS is working", "cors_enabled": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# Vercel serverless handler
handler = app
