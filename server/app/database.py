from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create database URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy engine with different settings for SQLite vs PostgreSQL
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite configuration (development)
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
    logger.info("Using SQLite database for development")
else:
    # PostgreSQL configuration (production-ready)
    connect_args = {}
    
    # Add SSL configuration for production
    if settings.database_ssl_config:
        connect_args.update(settings.database_ssl_config)
        logger.info(f"Using SSL connection with mode: {settings.DB_SSL_MODE}")
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        connect_args=connect_args,
        echo=settings.DEBUG
    )
    logger.info(f"Using PostgreSQL database with pool size: {settings.DB_POOL_SIZE}")

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database health check function
def check_database_health():
    """Check if database is accessible and healthy"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return True, "Database connection successful"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False, f"Database connection failed: {e}"

# Database initialization function
def init_database():
    """Initialize database tables"""
    try:
        # Import all models to ensure they're registered
        from app.models import user, course, sales, server_models_user, server_models_course, server_models_enrollment, server_models_content
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False 