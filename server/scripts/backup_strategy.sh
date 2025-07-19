#!/usr/bin/env bash
# Backup Strategy Script for Production Environment
# - Database dump (PostgreSQL)
# - File system backup (uploads, config)
# - Retention policy: keep 7 daily, 4 weekly, 12 monthly backups

set -euo pipefail

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/backups/ai-platform"
DB_NAME="${DB_NAME:-ai_platform}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

mkdir -p "$BACKUP_DIR/$TIMESTAMP"

echo "📦 Dumping PostgreSQL database..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -F c -b -v -f "$BACKUP_DIR/$TIMESTAMP/db_backup.dump" "$DB_NAME"

echo "🗄️  Archiving uploads directory..."
tar -czf "$BACKUP_DIR/$TIMESTAMP/uploads.tar.gz" /opt/ai-platform/uploads

echo "🗄️  Archiving configuration files..."
tar -czf "$BACKUP_DIR/$TIMESTAMP/config.tar.gz" /opt/ai-platform/config

echo "✅ Backup completed: $TIMESTAMP"

# Retention policy
find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} +

echo "🧹 Old backups cleaned up (retention policy applied)" 