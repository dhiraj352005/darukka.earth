from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the correct path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please check your .env file.")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_postgis():
    """
    Initialize PostGIS extension on database startup
    """
    with engine.connect() as connection:
        # Enable PostGIS extension
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        connection.commit()
        print("✓ PostGIS extension initialized successfully")


def create_tables():
    """
    Create all tables in the database
    """
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")
