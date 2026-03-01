# 🛠️ Quick Reference & Troubleshooting Guide

Fast problem-solving guide for developers and AI assistants working on Legal-Ease.

## 🚨 Critical Errors & Fixes

### Error: "Module not found: flask"

**Cause**: Virtual environment not activated or dependencies not installed  
**Fix**:
```bash
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

---

### Error: "No route matches '/'"

**Cause**: `index()` function missing `@app.route('/')` decorator  
**Fix**: [app.py](app.py) line ~80 - Add decorator:
```python
@app.route('/')
@app.route('/index')  # ← Add this line
def index():
    return render_template('index.html')
```

---

### Error: "Connection refused to localhost:5432"

**Cause**: PostgreSQL not running or DATABASE_URL not set  
**Fix**:
```bash
# Start PostgreSQL
sudo service postgresql start  # Linux
brew services start postgresql  # macOS

# Or use SQLite (default)
unset DATABASE_URL
python main.py
```

---

### Error: "tesseract is not installed" (OCR)

**Cause**: Tesseract binary missing  
**Fix**:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr libtesseract-dev

# macOS
brew install tesseract

# Also uncomment in requirements.txt:
# Pillow
# pytesseract
```

---

### Error: "Address already in use :5000"

**Cause**: Flask already running on that port  
**Fix**:
```bash
# Kill existing process
lsof -i :5000
kill -9 <PID>

# Or use different port
python main.py --port 5001
```

---

### Error: "CSRF token missing"

**Cause**: Form doesn't include CSRF token  
**Fix**: In HTML template, add to every form:
```html
<form method="POST">
    {{ csrf_token() }}
    <!-- form fields -->
</form>
```

---

### Error: "ModuleNotFoundError: No module named 'pytesseract'"

**Cause**: OCR dependency not installed  
**Fix**:
```bash
pip install pytesseract Pillow
pip freeze > requirements.txt
```

---

## ⚠️ Common Problems & Solutions

### Problem: Upload button not working

**Checklist**:
- [ ] Is `/upload` route defined in app.py?
- [ ] Does form have `enctype="multipart/form-data"`?
- [ ] Is file input named `file`?
- [ ] Is Flask app running?
- [ ] Check browser console for JavaScript errors (F12)

**Debug**:
```bash
# Verify route exists
curl -X POST http://localhost:5000/upload -F "file=@test.pdf" -v
```

---

### Problem: Summary not displaying

**Checklist**:
- [ ] Was text successfully extracted? (Check logs)
- [ ] Does utils.py have `summarize_legal_document()`?
- [ ] Is Sumy installed? `pip list | grep sumy`
- [ ] Does document have enough text? (>100 words)
- [ ] Are key_clauses being returned?

**Debug**:
```python
# Test summarization directly
from utils import summarize_legal_document

text = "This agreement is..."  # Sample text
result = summarize_legal_document(text)
print(result)  # Should show summary and clauses
```

---

### Problem: Database errors when saving

**Checklist**:
- [ ] Is database running?
- [ ] Is DATABASE_URL correct?
- [ ] Have you run `db.create_all()`?
- [ ] Are model relationships correct?

**Debug**:
```python
# Test database connection
from app import app, db
with app.app_context():
    db.session.execute("SELECT 1")
    print("✓ Database connected")
    db.create_all()
    print("✓ Tables created")
```

---

### Problem: "Permission denied" on uploads folder

**Cause**: uploads/ folder doesn't exist or wrong permissions  
**Fix**:
```bash
mkdir -p uploads
chmod 755 uploads

# Or in Python
import os
os.makedirs('uploads', exist_ok=True)
```

---

### Problem: Large PDF takes forever to process

**Solutions**:
1. Check PDF is not corrupted: `file contract.pdf`
2. Increase timeout: `app.config['UPLOAD_TIMEOUT'] = 60`
3. Split PDF: `pdftotext -f 1 -l 10 large.pdf text.txt`
4. Check system resources: `top` or `htop`

---

## 📊 Performance Optimization

### Slow Upload Processing

**Diagnosis**:
```python
# Add timing to utils.py
import time

def summarize_legal_document(text):
    start = time.time()
    # ... processing ...
    end = time.time()
    logging.info(f"Summarization took {end - start:.2f}s")
```

**Solutions by bottleneck**:

| Bottleneck | Duration | Solution |
|-----------|----------|----------|
| PDF extraction | 5-10s | Check file size, consider PyPDF2 |
| Tokenization | 2-3s | Sumy is slow, cache tokenizer |
| Summarization | 1-2s | Use fewer sentences, cache results |
| Database save | <1s | Use connection pooling, async writes |

### Memory Usage

```bash
# Monitor memory
python -m memory_profiler main.py

# Top memory hogs
from memory_profiler import profile

@profile
def process_large_file(filepath):
    # Will show line-by-line memory usage
    text = open(filepath).read()  # Might be slow
    ...
```

---

## 🔍 Debugging Techniques

### Enable Debug Logging

```python
# In app.py, set before running:
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('sqlalchemy').setLevel(logging.DEBUG)

app.run(debug=True)  # Shows request/response details
```

### Log Database Queries

```python
# See all SQL being executed
app.config['SQLALCHEMY_ECHO'] = True  # Only in development!
```

### Inspect Request/Response

```python
# Print incoming data
@app.before_request
def log_request():
    logging.info(f"Request: {request.method} {request.path}")
    logging.info(f"Headers: {dict(request.headers)}")
    logging.info(f"Data: {request.get_data()}")

@app.after_request
def log_response(response):
    logging.info(f"Response: {response.status_code}")
    return response
```

### Browser DevTools

**F12 to open DevTools**:
- **Console**: JavaScript errors and logs
- **Network**: See HTTP requests/responses
- **Application/Storage**: See cookies, localStorage
- **Performance**: Measure load times

---

## 🧪 Testing Quick Reference

### Run All Tests

```bash
pytest  # Runs all tests/ files
```

### Run Specific Test

```bash
pytest tests/test_utils.py::test_extract_text_from_pdf
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html tests/
# Open htmlcov/index.html in browser
```

### Write Quick Test

```python
# In tests/test_new.py
def test_my_feature():
    # Arrange
    expected = "result"
    
    # Act
    actual = my_function()
    
    # Assert
    assert actual == expected
```

---

## 🔐 Security Quick Checks

### Before Deployment

```bash
# Check for secrets in code
grep -r "password" --include="*.py" .
grep -r "secret" --include="*.py" .
grep -r "api_key" --include="*.py" .

# Should find NONE (all in .env)
```

**Fix**: Move all secrets to `.env.example`, add pattern to `.gitignore`

### Check Dependencies

```bash
# Find vulnerable packages
safety check -r requirements.txt

# Update if needed
pip install --upgrade <package>
```

### Test Authentication

```python
# Verify login required
@app.route('/upload')
@login_required  # ← Should have this
def upload_file():
    ...
```

---

## 📚 File Reference Quick Lookup

| Need to... | Edit this file |
|------------|----------------|
| Add a route | [app.py](app.py) line ~80 |
| Add processing logic | [utils.py](utils.py) |
| Add database model | [models.py](models.py) |
| Fix HTML | [templates/index.html](templates/index.html) |
| Fix styling | [static/css/style.css](static/css/style.css) |
| Fix JavaScript | [static/js/script.js](static/js/script.js) |
| Add dependency | [requirements.txt](requirements.txt) |
| Configure Flask | [app.py](app.py) top section |
| Add environment var | [.env.example](.env.example) |
| Deployment settings | [Procfile](Procfile), [DEPLOYMENT.md](DEPLOYMENT.md) |

---

## 🚀 Quick Commands

### Setup
```bash
python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### Run locally
```bash
python main.py
```

### Test
```bash
pytest -v
```

### Deploy
```bash
git add . && git commit -m "desc" && git push origin main
```

### Database reset
```bash
rm history.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Check app health
```bash
curl http://localhost:5000/
curl http://localhost:5000/history
curl -X POST http://localhost:5000/upload -F "file=@test.pdf"
```

---

## 🎯 Common Task Checklist

### Before Pushing Code
- [ ] Code runs locally without errors
- [ ] No hardcoded secrets or credentials
- [ ] Tests pass (or written new tests)
- [ ] No console.log or print statements
- [ ] PEP 8 compliant
- [ ] Commit message is clear

### Before Submitting PR
- [ ] Rebased on latest main
- [ ] No duplicate/merge commits
- [ ] CI checks passing
- [ ] Code review requested

### Before Deploying
- [ ] All PR reviews approved
- [ ] Tests passing on CI
- [ ] `.env` configured properly
- [ ] Procfile verified
- [ ] Rollback plan ready

---

## 📞 When to Ask for Help

**Ask when**:
- You're blocked for >30 minutes
- You need architecture decisions
- You're about to delete/modify production data
- You see a security concern
- Requirements are unclear

**Always mention**:
- What you tried
- Error message (full stack trace)
- What you expected to happen
- What actually happened

---

## 🔗 Useful Links

- [Flask Docs](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Bootstrap Docs](https://getbootstrap.com/docs/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [OWASP Security](https://owasp.org/)
- [Render Docs](https://render.com/docs)

---

## Last Used Command Patterns

```bash
# Activate environment
source venv/bin/activate

# Install/update packages
pip install -r requirements.txt --upgrade

# Run specific file
python utils.py  # Not typical, but for testing

# Database operations
python -c "code here"

# Git workflow
git checkout -b feature/name
git add .
git commit -m "type: description"
git push origin feature/name

# Testing
pytest tests/test_file.py -v

# Deployment
git push origin main  # Render auto-deploys
```

---

**Last Updated**: Feb 2026  
**Version**: 1.0  
**Maintained By**: Development Team
