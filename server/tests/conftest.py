import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.core.config import settings

# Use a test database URL if available, otherwise fallback to main DB
TEST_DATABASE_URL = getattr(settings, 'TEST_DATABASE_URL', None) or settings.DATABASE_URL

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False} if 'sqlite' in TEST_DATABASE_URL else {})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Yield a new database session for a test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine) 