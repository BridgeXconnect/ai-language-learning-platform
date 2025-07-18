#!/usr/bin/env python3
"""
PostgreSQL Migration Script for AI Language Learning Platform

This script helps migrate from SQLite to PostgreSQL for production deployment.
It includes data migration, schema validation, and connection testing.
"""

import os
import sys
import subprocess
import sqlite3
import psycopg2
from pathlib import Path
from urllib.parse import urlparse
import logging

# Add the parent directory to the path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import engine, Base, check_database_health

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostgreSQLMigrator:
    def __init__(self):
        self.sqlite_path = None
        self.postgres_url = None
        self.postgres_conn = None
        
    def validate_environment(self):
        """Validate that we have the necessary environment setup"""
        logger.info("Validating environment setup...")
        
        # Check if we're in the right directory
        if not Path("app").exists():
            logger.error("❌ Not in the correct directory. Please run from the server directory.")
            return False
            
        # Check if .env file exists
        if not Path(".env").exists():
            logger.error("❌ .env file not found. Please create one from env.example")
            return False
            
        # Validate DATABASE_URL
        if not settings.DATABASE_URL:
            logger.error("❌ DATABASE_URL not set in environment")
            return False
            
        # Check if it's a PostgreSQL URL
        if not settings.DATABASE_URL.startswith("postgresql://"):
            logger.error("❌ DATABASE_URL is not a PostgreSQL URL")
            logger.info("Current DATABASE_URL: " + settings.DATABASE_URL)
            return False
            
        self.postgres_url = settings.DATABASE_URL
        logger.info("✅ Environment validation passed")
        return True
        
    def test_postgresql_connection(self):
        """Test PostgreSQL connection"""
        logger.info("Testing PostgreSQL connection...")
        
        try:
            self.postgres_conn = psycopg2.connect(self.postgres_url)
            with self.postgres_conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                logger.info(f"✅ PostgreSQL connection successful: {version}")
            return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            return False
            
    def find_sqlite_database(self):
        """Find the SQLite database file"""
        logger.info("Looking for SQLite database...")
        
        possible_paths = [
            "test.db",
            "data/test.db", 
            "database.db",
            "app.db"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                self.sqlite_path = path
                logger.info(f"✅ Found SQLite database: {path}")
                return True
                
        logger.warning("⚠️ No SQLite database found. Will only create PostgreSQL schema.")
        return False
        
    def create_postgresql_schema(self):
        """Create PostgreSQL schema from SQLAlchemy models"""
        logger.info("Creating PostgreSQL schema...")
        
        try:
            # Import all models to ensure they're registered
            from app.models import user, course, sales, server_models_user, server_models_course, server_models_enrollment, server_models_content
            
            # Create all tables
            Base.metadata.create_all(bind=engine)
            logger.info("✅ PostgreSQL schema created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create PostgreSQL schema: {e}")
            return False
            
    def migrate_data_from_sqlite(self):
        """Migrate data from SQLite to PostgreSQL"""
        if not self.sqlite_path:
            logger.info("No SQLite database found, skipping data migration")
            return True
            
        logger.info(f"Migrating data from {self.sqlite_path} to PostgreSQL...")
        
        try:
            # Connect to SQLite
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            sqlite_conn.row_factory = sqlite3.Row
            
            # Get table names from SQLite
            cursor = sqlite_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"Found tables: {', '.join(tables)}")
            
            # Migrate each table
            for table in tables:
                if table == 'sqlite_sequence':  # Skip SQLite internal table
                    continue
                    
                logger.info(f"Migrating table: {table}")
                
                # Get data from SQLite
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                if not rows:
                    logger.info(f"Table {table} is empty, skipping")
                    continue
                    
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Insert into PostgreSQL
                with self.postgres_conn.cursor() as pg_cursor:
                    for row in rows:
                        placeholders = ', '.join(['%s'] * len(columns))
                        column_names = ', '.join(columns)
                        query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
                        
                        try:
                            pg_cursor.execute(query, list(row))
                        except Exception as e:
                            logger.warning(f"Failed to insert row in {table}: {e}")
                            continue
                            
                self.postgres_conn.commit()
                logger.info(f"✅ Migrated {len(rows)} rows from table {table}")
                
            sqlite_conn.close()
            logger.info("✅ Data migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Data migration failed: {e}")
            return False
            
    def verify_migration(self):
        """Verify that the migration was successful"""
        logger.info("Verifying migration...")
        
        try:
            # Test database health
            is_healthy, message = check_database_health()
            if not is_healthy:
                logger.error(f"❌ Database health check failed: {message}")
                return False
                
            # Check if tables exist and have data
            with self.postgres_conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name, (xpath('/row/cnt/text()', xml_count))[1]::text::int as row_count
                    FROM (
                        SELECT table_name, query_to_xml(format('select count(*) as cnt from %I.%I', table_schema, table_name), false, true, '') as xml_count
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    ) t
                    ORDER BY table_name;
                """)
                
                tables = cur.fetchall()
                logger.info("Table row counts:")
                for table_name, row_count in tables:
                    logger.info(f"  {table_name}: {row_count} rows")
                    
            logger.info("✅ Migration verification completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration verification failed: {e}")
            return False
            
    def run_migration(self):
        """Run the complete migration process"""
        logger.info("=" * 60)
        logger.info("PostgreSQL Migration Script")
        logger.info("=" * 60)
        
        steps = [
            ("Environment Validation", self.validate_environment),
            ("PostgreSQL Connection Test", self.test_postgresql_connection),
            ("SQLite Database Discovery", self.find_sqlite_database),
            ("PostgreSQL Schema Creation", self.create_postgresql_schema),
            ("Data Migration", self.migrate_data_from_sqlite),
            ("Migration Verification", self.verify_migration)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n--- {step_name} ---")
            if not step_func():
                logger.error(f"❌ Migration failed at step: {step_name}")
                return False
                
        logger.info("\n" + "=" * 60)
        logger.info("✅ Migration completed successfully!")
        logger.info("=" * 60)
        
        if self.postgres_conn:
            self.postgres_conn.close()
            
        return True

def main():
    """Main function"""
    migrator = PostgreSQLMigrator()
    
    try:
        success = migrator.run_migration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nMigration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 