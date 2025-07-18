# 🚀 AI Language Learning Platform - Deployment Guide

> **Single Source of Truth** - This is the ONLY deployment guide you need to follow.

## 📋 Quick Start (5 minutes)

1. **Run the setup script**: `./deployment/setup.sh`
2. **Follow the automated prompts** to configure your services
3. **Deploy**: `./deployment/deploy.sh`

## 🎯 Deployment Strategy

### **Simple & Reliable Approach**
- **Frontend**: Vercel (Next.js) - Zero config, automatic deployments
- **Backend**: Render (FastAPI) - Simple Python hosting
- **Database**: Supabase (PostgreSQL) - Managed database with real-time features
- **AI Agents**: Render (Python services) - Same platform as backend

### **Why This Approach?**
- ✅ **No server management** - Everything is managed
- ✅ **Automatic scaling** - Handles traffic spikes
- ✅ **Built-in monitoring** - No setup required
- ✅ **Cost effective** - Free tiers available
- ✅ **Reliable** - 99.9% uptime guaranteed

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Vercel)      │◄──►│   (Render)      │◄──►│   (Supabase)    │
│   Next.js       │    │   FastAPI       │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Agents     │    │   Monitoring    │    │   Analytics     │
│   (Render)      │    │   (Built-in)    │    │   (Built-in)    │
│   Python        │    │   Logs/Metrics  │    │   Usage Stats   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 File Structure

```
deployment/
├── setup.sh              # Initial setup script
├── deploy.sh             # Deployment script
├── config/
│   ├── vercel.json       # Vercel configuration
│   ├── render.yaml       # Render configuration
│   └── supabase.sql      # Database schema
├── scripts/
│   ├── health-check.sh   # Health check script
│   └── rollback.sh       # Rollback script
└── docs/
    ├── troubleshooting.md # Common issues
    └── monitoring.md     # Monitoring guide
```

## 🚀 Step-by-Step Deployment

### **Phase 1: Setup (5 minutes)**

1. **Run Setup Script**
   ```bash
   ./deployment/setup.sh
   ```

2. **Configure Services**
   - Follow the prompts to set up Vercel, Render, and Supabase
   - The script will guide you through each step

3. **Verify Setup**
   ```bash
   ./deployment/scripts/health-check.sh
   ```

### **Phase 2: Deploy (2 minutes)**

1. **Deploy to Staging**
   ```bash
   ./deployment/deploy.sh staging
   ```

2. **Test Everything**
   - Frontend: https://your-app-staging.vercel.app
   - Backend: https://your-backend-staging.onrender.com
   - Database: Check Supabase dashboard

3. **Deploy to Production**
   ```bash
   ./deployment/deploy.sh production
   ```

## 🔧 Configuration

### **Environment Variables**

#### Frontend (Vercel)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

#### Backend (Render)
```bash
DATABASE_URL=postgresql://your-supabase-connection-string
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
ENVIRONMENT=production
CORS_ORIGINS=https://your-domain.vercel.app
```

#### AI Agents (Render)
```bash
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
DATABASE_URL=postgresql://your-supabase-connection-string
ORCHESTRATOR_URL=https://your-orchestrator.onrender.com
```

## 📊 Monitoring & Health Checks

### **Automatic Monitoring**
- **Vercel**: Built-in analytics and performance monitoring
- **Render**: Automatic health checks and logs
- **Supabase**: Database monitoring and alerts

### **Manual Health Checks**
```bash
# Check all services
./deployment/scripts/health-check.sh

# Check specific service
./deployment/scripts/health-check.sh frontend
./deployment/scripts/health-check.sh backend
./deployment/scripts/health-check.sh database
```

## 🔄 CI/CD Pipeline

### **Automatic Deployments**
- **Push to `main`** → Deploy to production
- **Push to `develop`** → Deploy to staging
- **Pull Request** → Run tests only

### **Manual Deployments**
```bash
# Deploy specific branch
./deployment/deploy.sh production main

# Deploy with custom config
./deployment/deploy.sh production --config custom.env
```

## 🛠️ Troubleshooting

### **Common Issues**

1. **Build Failures**
   ```bash
   # Check logs
   ./deployment/scripts/check-logs.sh
   
   # Rebuild
   ./deployment/scripts/rebuild.sh
   ```

2. **Database Connection Issues**
   ```bash
   # Test connection
   ./deployment/scripts/test-db.sh
   
   # Reset connection
   ./deployment/scripts/reset-db.sh
   ```

3. **Environment Variable Issues**
   ```bash
   # Validate environment
   ./deployment/scripts/validate-env.sh
   
   # Update variables
   ./deployment/scripts/update-env.sh
   ```

### **Rollback**
```bash
# Rollback to previous version
./deployment/scripts/rollback.sh

# Rollback specific service
./deployment/scripts/rollback.sh frontend
```

## 💰 Cost Breakdown

### **Monthly Costs (Approximate)**
- **Vercel**: $0-20 (free tier usually sufficient)
- **Render**: $7-25 (depending on usage)
- **Supabase**: $0-25 (free tier for small apps)
- **Domain**: $10-15/year
- **Total**: ~$7-70/month

### **Free Tier Limits**
- **Vercel**: 100GB bandwidth, 100 serverless function executions
- **Render**: 750 hours/month, 512MB RAM
- **Supabase**: 500MB database, 50,000 monthly active users

## 🔒 Security

### **Best Practices**
- ✅ Environment variables for all secrets
- ✅ HTTPS enforced everywhere
- ✅ CORS properly configured
- ✅ Database connection pooling
- ✅ Rate limiting on APIs

### **Security Checklist**
```bash
# Run security audit
./deployment/scripts/security-audit.sh

# Check for vulnerabilities
./deployment/scripts/vulnerability-scan.sh
```

## 📈 Scaling

### **Automatic Scaling**
- **Vercel**: Automatic scaling based on traffic
- **Render**: Automatic scaling with custom rules
- **Supabase**: Automatic scaling with usage

### **Manual Scaling**
```bash
# Scale backend
./deployment/scripts/scale.sh backend 2

# Scale AI agents
./deployment/scripts/scale.sh agents 3
```

## 🆘 Support

### **Getting Help**
1. **Check logs**: `./deployment/scripts/check-logs.sh`
2. **Run diagnostics**: `./deployment/scripts/diagnostics.sh`
3. **View troubleshooting guide**: `deployment/docs/troubleshooting.md`

### **Emergency Contacts**
- **Vercel Support**: https://vercel.com/support
- **Render Support**: https://render.com/docs/help
- **Supabase Support**: https://supabase.com/support

## 📝 Maintenance

### **Regular Tasks**
- **Weekly**: Check logs and performance
- **Monthly**: Update dependencies
- **Quarterly**: Security audit
- **Annually**: Review costs and scaling

### **Automated Maintenance**
```bash
# Update dependencies
./deployment/scripts/update-deps.sh

# Backup database
./deployment/scripts/backup.sh

# Clean up old deployments
./deployment/scripts/cleanup.sh
```

---

## 🎯 Next Steps

1. **Run the setup script**: `./deployment/setup.sh`
2. **Follow the prompts** to configure your services
3. **Deploy to staging**: `./deployment/deploy.sh staging`
4. **Test everything** thoroughly
5. **Deploy to production**: `./deployment/deploy.sh production`

**Need help?** Check the troubleshooting guide or run `./deployment/scripts/help.sh`

---

*Last updated: $(date)*
*Version: 1.0.0* 