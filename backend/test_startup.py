"""
Test script to verify the FastAPI application can start successfully
"""
import sys
sys.path.insert(0, '.')

try:
    print("Testing imports...")
    from database import init_postgis, create_tables, engine
    from models import User, Project, Site
    from routes_auth import router as auth_router
    from routes_projects import router as projects_router
    from routes_sites import router as sites_router
    from main import app
    
    print("✓ All imports successful")
    
    print("\nTesting database connection...")
    with engine.connect() as connection:
        result = connection.execute("SELECT version();")
        version = result.fetchone()[0]
        print(f"✓ Database connected: {version[:50]}...")
    
    print("\nInitializing PostGIS...")
    init_postgis()
    
    print("\nCreating database tables...")
    create_tables()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nFastAPI application is ready to run.")
    print("Start the server with:")
    print("  cd backend")
    print("  ..\\backend\\venv\\Scripts\\uvicorn main:app --reload")
    print("\nOr from the project root:")
    print("  backend\\venv\\Scripts\\uvicorn main:app --reload --app-dir backend")
    print("\nAPI Documentation will be available at:")
    print("  http://localhost:8000/docs")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
