# 🔧 Environment Setup Guide

Complete instructions for setting up Legal-Ease development and production environments.

## Prerequisites

- **Python**: 3.11 or higher
- **Git**: For version control
- **PostgreSQL**: 12+ (optional, for production-like testing)
- **System Package Manager**: apt (Ubuntu/Debian) or brew (macOS)

## 🖥️ Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Shards-Of-Sapphire/Legal-Ease.git
cd Legal-Ease
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

### 3. Install Core Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install from requirements
pip install -r requirements.txt
```

### 4. Install Optional Dependencies (for OCR/Camera Support)

```bash
# On Ubuntu/Debian:
sudo apt-get install tesseract-ocr libtesseract-dev

# On macOS (using Homebrew):
brew install tesseract

# Then install Python packages:
pip install Pillow pytesseract
```

### 5. Set Environment Variables

Create a `.env` file in the project root:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SESSION_SECRET=your-secret-key-here-min-32-chars-random

# Database (optional for local - uses SQLite by default)
# DATABASE_URL=sqlite:///history.db

# Optional: For production-like testing
# DATABASE_URL=postgresql://user:password@localhost:5432/legal_ease_db
```

Or set them in your shell:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
export SESSION_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')
```

### 6. Initialize Database

```bash
# For local SQLite (automatic):
python main.py

# The database will be created in `history.db`
```

### 7. Run Development Server

```bash
python main.py
```

Access the app at: `http://localhost:5000`

## 🐳 Docker Development (Optional)

If you prefer containerized development:

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir Pillow pytesseract

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "main.py"]
```

### Run with Docker

```bash
# Build image
docker build -t legal-ease:latest .

# Run container
docker run -p 5000:5000 \
  -e SESSION_SECRET="your-secret" \
  -e FLASK_ENV=development \
  legal-ease:latest
```

## 🗄️ PostgreSQL Setup (Production-like)

For testing with PostgreSQL locally:

### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql@15
```

### 2. Create Database and User

```bash
# Access PostgreSQL
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE legal_ease_db;
CREATE USER legal_ease_user WITH PASSWORD 'secure_password_here';
ALTER ROLE legal_ease_user SET client_encoding TO 'utf8';
ALTER ROLE legal_ease_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE legal_ease_user SET default_transaction_deferrable TO on;
ALTER ROLE legal_ease_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE legal_ease_db TO legal_ease_user;
\q
```

### 3. Set Environment Variable

```bash
export DATABASE_URL=postgresql://legal_ease_user:secure_password_here@localhost:5432/legal_ease_db
```

### 4. Verify Connection

```bash
python -c "
from app import app
with app.app_context():
    from sqlalchemy import text
    result = app.config['SQLALCHEMY_DATABASE_URI']
    print(f'Database configured: {result}')
"
```

## ☁️ Render Deployment Setup

### 1. Prepare Repository

```bash
# Ensure Procfile is correct
cat Procfile
# Should show: web: gunicorn app:app
```

### 2. Set Environment Variables on Render

In your Render service dashboard, set:

```
SESSION_SECRET=<generate-32-char-random-string>
FLASK_ENV=production
DATABASE_URL=<provided-by-render-for-postgresql>
```

### 3. Add PostgreSQL Database

1. Go to Render Dashboard
2. Create new PostgreSQL database
3. Copy the DATABASE_URL
4. Add to environment variables

### 4. Deploy

```bash
git push origin main
# Automatic deployment triggers
```

## 🔐 Production Environment Variables

For production deployment, ensure these are set:

| Variable | Purpose | Example |
|----------|---------|---------|
| `SESSION_SECRET` | Flask session encryption | `abc123...` (32+ chars) |
| `FLASK_ENV` | Environment mode | `production` |
| `DATABASE_URL` | Database connection | `postgresql://user:pass@host/db` |
| `FLASK_DEBUG` | Debug mode | `0` (must be 0 in production) |

**Never** commit these to git. Use Render's environment variable UI.

## 🧹 Cleanup & Maintenance

### Clear Cache

```bash
# Remove Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name '*.pyc' -delete

# Remove virtual environment packages
pip cache purge
```

### Reset Database

**WARNING**: This deletes all data!

```bash
# SQLite
rm history.db

# PostgreSQL (from psql)
DROP DATABASE legal_ease_db;
CREATE DATABASE legal_ease_db;
```

### Update Dependencies

```bash
# Update pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Update all packages to latest compatible versions
pip install --upgrade -r requirements.txt
```

## ✅ Verification Checklist

After setup, verify everything works:

```bash
# Check Python version
python --version  # Should be 3.11+

# Check virtual environment
which python  # Should show venv path

# Check Flask installation
python -c "import flask; print(flask.__version__)"

# Check database initialization
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✓ Database initialized')
"

# Check imports
python -c "
import utils
import models
print('✓ All imports successful')
"

# Test development server
python main.py  # Should show Flask running on http://127.0.0.1:5000/
```

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Issue: `tesseract is not installed` (OCR errors)

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr libtesseract-dev

# macOS
brew install tesseract

# Then verify:
tesseract --version
```

### Issue: `Could not connect to database`

**Solution**:
```bash
# Check DATABASE_URL is set
echo $DATABASE_URL

# For PostgreSQL, ensure service is running:
# Ubuntu
sudo service postgresql start

# macOS
brew services start postgresql

# Test connection:
psql $DATABASE_URL -c "SELECT 1;"
```

### Issue: `Address already in use (port 5000)`

**Solution**:
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process:
kill -9 <PID>

# Or use different port:
FLASK_ENV=development python main.py --port 5001
```

### Issue: `CSRF token missing` in forms

**Solution**: Ensure Flask-WTF is installed:
```bash
pip install Flask-WTF
```

And templates include CSRF token:
```html
<form method="POST">
    {{ csrf_token() }}
    <!-- form fields -->
</form>
```

## 📚 Development Workflow

### For Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Install branch-specific dependencies (if any)
pip install -r requirements.txt

# 3. Run tests (when available)
pytest tests/

# 4. Run the app
python main.py

# 5. Commit and push
git add .
git commit -m "feat: description of feature"
git push origin feature/your-feature-name
```

### For Bug Fixes

```bash
# 1. Create fix branch
git checkout -b fix/bug-description

# 2. Run specific test (if available)
pytest tests/test_specific.py

# 3. Make changes, test locally
python main.py

# 4. Commit and push
git add .
git commit -m "fix: description of fix"
git push origin fix/bug-description
```

## 🚀 Quick Start Command Reference

```bash
# Most common development commands:

# Setup (one time)
python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Development (daily)
python main.py

# Database operations
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Database reset
rm history.db

# Run with different port
FLASK_ENV=development python main.py --port 5001
```

---

**Last Updated**: Feb 2026  
**Version**: 1.0  
**Maintainer**: Development Team
