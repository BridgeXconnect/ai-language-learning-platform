"""
Database Migration Script for Production Deployment.
Run this script on the production server to apply the latest Alembic migrations and seed initial data.
"""

import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ALEMBIC_CFG = BASE_DIR / "alembic.ini"


def run_command(cmd: str):
    """Run a shell command and exit on failure."""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        sys.exit(result.returncode)


def migrate():
    """Apply Alembic migrations."""
    if not ALEMBIC_CFG.exists():
        print("alembic.ini not found – ensure Alembic is configured")
        sys.exit(1)
    run_command(f"alembic -c {ALEMBIC_CFG} upgrade head")


def seed():
    """Seed production data using init_db.py."""
    run_command("python -m app.init_db")


def main():
    migrate()
    seed()
    print("✅ Production database migrated and seeded successfully")


if __name__ == "__main__":
    main() 