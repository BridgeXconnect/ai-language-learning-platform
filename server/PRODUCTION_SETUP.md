# 🚀 Production Setup Guide - AI Language Learning Platform

## Overview

This guide provides step-by-step instructions for deploying the AI Language Learning Platform to production with enterprise-grade features including PostgreSQL, SSL, monitoring, and automated deployment.

## 📋 Prerequisites

- **Server**: Ubuntu 20.04+ or CentOS 8+ (recommended: 4GB RAM, 2 vCPUs)
- **Domain**: Configured with DNS pointing to your server
- **SSL Certificate**: Let's Encrypt or commercial certificate
- **Database**: Supabase PostgreSQL (already configured)
- **Python**: 3.9+ with virtual environment

## 🛠️ Step 1: Server Preparation

### 1.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx redis-server
```

### 1.2 Create Application User
```bash
sudo useradd -m -s /bin/bash aiapp
sudo usermod -aG sudo aiapp
sudo passwd aiapp
```

### 1.3 Setup Application Directory
```bash
sudo mkdir -p /opt/ai-language-platform
sudo chown aiapp:aiapp /opt/ai-language-platform
```

## 🗄️ Step 2: Database Configuration

### 2.1 Verify Supabase Connection
Your Supabase PostgreSQL database is already configured with:
- **Host**: `aws-0-ap-southeast-1.pooler.supabase.com`
- **Port**: `5432`
- **Database**: `postgres`
- **Username**: `postgres.qpxvicjunijsydgigmmd`

### 2.2 Test Connection
```bash
cd /opt/ai-language-platform
python -c "from app.main import app; print('Database connection successful')"
```

## 🔧 Step 3: Application Deployment

### 3.1 Clone Application
```bash
cd /opt/ai-language-platform
git clone <your-repo-url> .
```

### 3.2 Setup Python Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3 Install Production Dependencies
```bash
pip install gunicorn uvicorn[standard] psycopg2-binary redis celery
```

### 3.4 Configure Environment
```bash
cp .env.production .env
# Edit .env with your production values
nano .env
```

## 🔐 Step 4: Security Configuration

### 4.1 Generate Secure Secrets
```bash
python -c "
import secrets
print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))
print('API_SECRET_KEY=' + secrets.token_urlsafe(32))
"
```

### 4.2 Update Environment Variables
```bash
# Add to .env file:
JWT_SECRET_KEY=your_generated_secret
ENVIRONMENT=production
DEBUG=False
```

### 4.3 Configure CORS
Update `CORS_ORIGINS` in `.env`:
```bash
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

## 🚀 Step 5: Service Configuration

### 5.1 Create Systemd Service
```bash
sudo tee /etc/systemd/system/ai-language-platform.service << EOF
[Unit]
Description=AI Language Learning Platform
After=network.target

[Service]
Type=exec
User=aiapp
Group=aiapp
WorkingDirectory=/opt/ai-language-platform
Environment=PATH=/opt/ai-language-platform/.venv/bin
ExecStart=/opt/ai-language-platform/.venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### 5.2 Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-language-platform
sudo systemctl start ai-language-platform
sudo systemctl status ai-language-platform
```

## 🌐 Step 6: Nginx Configuration

### 6.1 Create Nginx Configuration
```bash
sudo tee /etc/nginx/sites-available/ai-language-platform << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static/ {
        alias /opt/ai-language-platform/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
```

### 6.2 Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/ai-language-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Step 7: SSL Configuration

### 7.1 Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 7.2 Obtain SSL Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 7.3 Auto-renewal
```bash
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Step 8: Monitoring & Logging

### 8.1 Setup Logging
```bash
sudo mkdir -p /var/log/ai-language-platform
sudo chown aiapp:aiapp /var/log/ai-language-platform
```

### 8.2 Configure Log Rotation
```bash
sudo tee /etc/logrotate.d/ai-language-platform << EOF
/var/log/ai-language-platform/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 aiapp aiapp
    postrotate
        systemctl reload ai-language-platform
    endscript
}
EOF
```

### 8.3 Health Check Endpoint
The application includes a health check at `/health`:
```bash
curl https://yourdomain.com/health
```

## 🔄 Step 9: Automated Deployment

### 9.1 Run Deployment Script
```bash
cd /opt/ai-language-platform
python scripts/deploy_production.py
```

### 9.2 Verify Deployment
```bash
# Check service status
sudo systemctl status ai-language-platform

# Check logs
sudo journalctl -u ai-language-platform -f

# Test API endpoints
curl https://yourdomain.com/health
curl https://yourdomain.com/docs
```

## 🧪 Step 10: Testing

### 10.1 API Testing
```bash
# Health check
curl https://yourdomain.com/health

# API documentation
curl https://yourdomain.com/docs

# Test authentication
curl -X POST https://yourdomain.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","username":"testuser"}'
```

### 10.2 Database Testing
```bash
# Test database connection
python -c "from app.database import engine; print('Database connected:', engine.url)"

# Test model creation
python -c "from app.models import Base; from app.database import engine; Base.metadata.create_all(bind=engine)"
```

## 🔧 Step 11: Performance Optimization

### 11.1 Database Connection Pooling
The application is configured with:
- **Pool Size**: 10 connections
- **Max Overflow**: 20 connections
- **Pool Timeout**: 30 seconds
- **Pool Recycle**: 1800 seconds

### 11.2 Redis Caching (Optional)
```bash
# Install Redis
sudo apt install -y redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set: maxmemory 256mb
# Set: maxmemory-policy allkeys-lru

sudo systemctl restart redis
```

### 11.3 Background Tasks (Optional)
```bash
# Install Celery
pip install celery redis

# Start Celery worker
celery -A app.celery_app worker --loglevel=info
```

## 🛡️ Step 12: Security Hardening

### 12.1 Firewall Configuration
```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 12.2 Fail2ban Configuration
```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 12.3 Regular Updates
```bash
# Create update script
sudo tee /opt/update-system.sh << EOF
#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo systemctl restart ai-language-platform
sudo systemctl restart nginx
EOF

sudo chmod +x /opt/update-system.sh
```

## 📈 Step 13: Monitoring & Alerts

### 13.1 Basic Monitoring
```bash
# Monitor service status
watch -n 5 'systemctl status ai-language-platform'

# Monitor logs
tail -f /var/log/ai-language-platform/app.log

# Monitor system resources
htop
```

### 13.2 Health Check Script
```bash
sudo tee /opt/health-check.sh << EOF
#!/bin/bash
if ! curl -f https://yourdomain.com/health > /dev/null 2>&1; then
    echo "Health check failed at \$(date)" >> /var/log/ai-language-platform/health.log
    sudo systemctl restart ai-language-platform
fi
EOF

sudo chmod +x /opt/health-check.sh
# Add to crontab: */5 * * * * /opt/health-check.sh
```

## 🔄 Step 14: Backup Strategy

### 14.1 Database Backup
```bash
# Create backup script
sudo tee /opt/backup-db.sh << EOF
#!/bin/bash
BACKUP_DIR="/opt/backups/\$(date +%Y%m%d)"
mkdir -p \$BACKUP_DIR
pg_dump \$DATABASE_URL > \$BACKUP_DIR/database_backup.sql
tar -czf \$BACKUP_DIR/database_backup.tar.gz \$BACKUP_DIR/database_backup.sql
rm \$BACKUP_DIR/database_backup.sql
find /opt/backups -type d -mtime +7 -exec rm -rf {} \;
EOF

sudo chmod +x /opt/backup-db.sh
# Add to crontab: 0 2 * * * /opt/backup-db.sh
```

### 14.2 Application Backup
```bash
# Backup application files
sudo tar -czf /opt/backups/app_backup_\$(date +%Y%m%d).tar.gz /opt/ai-language-platform
```

## 🚨 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   sudo journalctl -u ai-language-platform -f
   sudo systemctl status ai-language-platform
   ```

2. **Database connection issues**
   ```bash
   python -c "from app.database import engine; print(engine.url)"
   ```

3. **Permission issues**
   ```bash
   sudo chown -R aiapp:aiapp /opt/ai-language-platform
   sudo chmod -R 755 /opt/ai-language-platform
   ```

4. **Nginx issues**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

### Log Locations
- **Application logs**: `/var/log/ai-language-platform/`
- **System logs**: `sudo journalctl -u ai-language-platform`
- **Nginx logs**: `/var/log/nginx/`
- **System logs**: `/var/log/syslog`

## 📞 Support

For issues or questions:
1. Check the logs first
2. Verify configuration files
3. Test individual components
4. Review this guide

## 🎉 Success!

Your AI Language Learning Platform is now deployed in production with:
- ✅ PostgreSQL database (Supabase)
- ✅ SSL encryption
- ✅ Nginx reverse proxy
- ✅ Systemd service management
- ✅ Automated deployment
- ✅ Monitoring and logging
- ✅ Security hardening
- ✅ Backup strategy

**Next Steps:**
1. Update DNS to point to your server
2. Test all API endpoints
3. Configure monitoring alerts
4. Set up CI/CD pipeline
5. Document your specific configuration

---

*Last updated: July 12, 2025* 