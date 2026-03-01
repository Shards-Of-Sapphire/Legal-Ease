# 🚀 Deployment Guide

Step-by-step instructions for deploying Legal-Ease to production on Render.

## Pre-Deployment Checklist

Before deploying, ensure:

- [ ] All critical bugs fixed (Week 1 tasks complete)
- [ ] Security measures implemented (Week 2 tasks)
- [ ] Tests passing locally
- [ ] No console.log or print statements left
- [ ] `.env` file NOT committed to git
- [ ] `FLASK_DEBUG = False` in production
- [ ] `SESSION_SECRET` is strong (32+ random chars)
- [ ] Database URL configured
- [ ] Procfile correct: `web: gunicorn app:app`
- [ ] requirements.txt updated
- [ ] All environment variables documented

---

## Render Deployment

### Step 1: Prepare Repository

**1.1 Ensure Procfile is correct**:
```plaintext
web: gunicorn app:app
```

**1.2 Check requirements.txt**:
```bash
# All dependencies listed
cat requirements.txt | grep -E "^[a-z]"
```

**1.3 Verify .gitignore**:
```bash
# Should include:
# .env
# __pycache__/
# *.pyc
# venv/
# uploads/*
# *.db
```

**1.4 Test locally**:
```bash
# Simulate production
export FLASK_ENV=production
export FLASK_DEBUG=0
gunicorn app:app
# Should see: "Starting gunicorn 23.0.0"
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository (Legal-Ease)
3. Select branch: `main`

**Configure Service**:
- **Name**: `legal-ease`
- **Environment**: `Python 3.11`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Instance Type**: `Free` (or paid for production)

### Step 4: Set Environment Variables

In the Render dashboard:

```
SESSION_SECRET=<generate-32-char-random-string>
FLASK_ENV=production
FLASK_DEBUG=0
```

**Generate secure SESSION_SECRET**:
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
# Copy output and paste in Render UI
```

### Step 5: Create PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Name: `legal-ease-db`
3. Region: Same as web service
4. PostgreSQL Version: 15+
5. Plan: Free (or paid for production)

**Copy DATABASE_URL** from database dashboard.

Add to web service environment variables:
```
DATABASE_URL=postgres://user:pass@host:5432/dbname
```

### Step 6: Deploy

1. Click "Create Web Service"
2. Render automatically starts building
3. Watch logs for errors

**Logs should show**:
```
=== Building ===
Running build command: pip install -r requirements.txt
... (installing packages)
Build completed successfully

=== Starting services ===
Starting web process...
Listening on 0.0.0.0:10000
```

### Step 7: Verify Deployment

```bash
# Test health check
curl https://legal-ease-xxxx.onrender.com/

# Test upload endpoint
curl -X POST https://legal-ease-xxxx.onrender.com/upload \
  -F "file=@test.pdf" \
  -L
```

---

## Database Migration

### First Time Setup

If deploying for the first time:

```bash
# Render runs build command
pip install -r requirements.txt

# Database creates automatically when app starts
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✓ Database created')
"
```

### Existing Database

If migrating from SQLite to PostgreSQL:

```bash
# Export from SQLite (local)
python scripts/export_data.py > data.json

# Import to PostgreSQL (on Render after deploy)
python scripts/import_data.py < data.json
```

### Schema Updates (Future)

When models change, use migrations:

```bash
# Install Flask-Migrate
pip install Flask-Migrate

# Create migration
flask db migrate -m "Add user authentication"

# Apply migration
flask db upgrade

# Push to git
git add migrations/
git commit -m "chore: add user auth migration"
git push origin main
```

---

## Post-Deployment Steps

### 1. Verify Data Loading

```bash
# Check database connected
curl https://legal-ease.onrender.com/history

# Should show documents (if any exist)
```

### 2. Check Logs

In Render dashboard:
- **Logs** tab should show no errors
- **Events** tab shows deployment history
- Watch for 5xx errors in first hour

### 3. Run Health Checks

```bash
# Home page loads
curl https://legal-ease.onrender.com/ -I
# Should return 200 OK

# Upload works
curl -X POST https://legal-ease.onrender.com/upload \
  -F "file=@test_document.pdf" \
  --progress-bar

# History endpoint responds
curl https://legal-ease.onrender.com/history -I
# Should return 200 OK
```

### 4. Monitor Performance

- Check response times
- Monitor error rates
- Set up email notifications for crashes

**In Render dashboard**:
- Metrics → Response Time
- Logs → Error count
- Alerts → Email on 500 errors

---

## Troubleshooting Deployment

### Issue: Build fails with "ModuleNotFoundError"

**Solution**:
```bash
# The package isn't in requirements.txt
pip install <missing_package>
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: add missing dependency"
git push origin main
# Render auto-redeploys
```

### Issue: "DATABASE_URL not set"

**Solution**:
1. Go to Render dashboard
2. Web service → Environment
3. Add `DATABASE_URL=postgres://...`
4. Manually trigger deploy or push to git

### Issue: Runtime crashes with 502 Bad Gateway

**Solution**:
```bash
# Check logs for errors
# Common causes:
# 1. Gunicorn command wrong
# 2. Flask app import failing
# 3. Database connection timeout

# Test locally first:
gunicorn app:app
# Should say "Listening on 0.0.0.0:8000"
```

### Issue: PDF extraction times out

**Solution**:
1. Increase web service timeout (if paid tier):
   - Health check: 30 seconds
   - Request timeout: 120 seconds

2. Optimize code:
   - Add streaming for large files
   - Process async with Celery (future)

### Issue: Running out of disk space

This shouldn't happen on Render, but if it does:
- Delete old uploaded files: `rm uploads/*`
- Clear database: Not recommended without backup

Render provides 1GB ephemeral storage (deleted on restart).

---

## Scaling Considerations

### Current Setup (Free Tier)
- 1 web dyno (512MB RAM, 0.5 CPU)
- Shared PostgreSQL (512MB)
- Suitable for: <100 concurrent users

### Production Setup (Paid Tier)
- Standard-1x dyno (512MB, 1x speed)
- Standard PostgreSQL (4GB)
- More suitable for: <1000 users

### High Scale (Multiple Dynos)
- Scale to 2+ dynos
- Load balancer
- Dedicated database
- Redis caching
- Celery workers

```yaml
# docker-compose.yml for local production simulation
version: '3'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/legal_ease
      - FLASK_ENV=production
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=legal_ease
      - POSTGRES_USER=legal_ease_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
volumes:
  postgres_data:
```

Run with: `docker-compose up`

---

## Monitoring & Maintenance

### Daily Checks
- [ ] App is running (no 500 errors)
- [ ] Database is responding
- [ ] Response times are normal

### Weekly Checks
- [ ] Review error logs
- [ ] Check database size
- [ ] Verify backups working

### Monthly Checks
- [ ] Update dependencies:
  ```bash
  pip list --outdated
  pip install --upgrade -r requirements.txt
  ```
- [ ] review security advisories:
  ```bash
  safety check -r requirements.txt
  ```
- [ ] Database optimization:
  ```bash
  VACUUM; ANALYZE;  # PostgreSQL
  ```

### Quarterly
- [ ] Full security audit
- [ ] Performance review
- [ ] Backup restoration test
- [ ] Disaster recovery plan update

---

## Rollback Procedure

If deployment breaks production:

```bash
# Render keeps previous deployments for 1 hour

# Option 1: Revert git commit
git revert HEAD
git push origin main
# Render auto-redeploys previous version

# Option 2: Manually rollback in Render dashboard
# Deployments tab → Select previous working version → Redeploy
```

---

## CI/CD Pipeline (Future)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run tests
        run: |
          python -m pytest tests/
          
      - name: Security scan
        run: |
          safety check -r requirements.txt
          
      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          curl -X POST https://api.render.com/deploy \
            -H "Authorization: Bearer $RENDER_API_KEY"
```

---

## Disaster Recovery

### Backup Strategy
- Automated daily backups (Render PostgreSQL)
- Manual exports weekly:
  ```bash
  pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
  ```

### Recovery Procedure
```bash
# If data is corrupted:

# 1. Restore from backup
psql $DATABASE_URL < backup_20260228.sql

# 2. Verify data integrity
python scripts/validate_data.py

# 3. Restart app
git push origin main  # Triggers redeploy
```

---

## Cost Estimation

| Component | Free Tier | Starter | Standard |
|-----------|-----------|---------|----------|
| Web | $0 | $7/mo | $12/mo |
| PostgreSQL | $0 | $15/mo | $30/mo |
| Storage | 1GB ephemeral | 100GB | 500GB |
| Bandwidth | Limited | 100GB/mo | Unlimited |
| **Total** | **$0** | **$22/mo** | **$42/mo** |

**Recommendation for MVP**: Start free tier, upgrade to Starter when hitting limits.

---

## Support & Issues

If deployment fails:

1. Check Render logs (Dashboard → Logs tab)
2. Test locally: `gunicorn app:app`
3. Verify environment variables
4. Check requirements.txt
5. Email support with logs

---

**Last Updated**: Feb 2026  
**Version**: 1.0  
**Maintainer**: DevOps Team
