# 🔒 Security Policy & Guidelines

Security considerations, threat model, and best practices for Legal-Ease development and deployment.

## Security Philosophy

**Core Principles**:
1. **Privacy First** - User documents are confidential
2. **Least Privilege** - Users see only their own data
3. **Defense in Depth** - Multiple security layers
4. **Fail Safely** - Errors don't reveal sensitive info
5. **Audit Everything** - Log security-relevant events

## Threat Model

### Assets to Protect

| Asset | Value | Threat |
|-------|-------|--------|
| User Documents | HIGH | Data breach, unauthorized access |
| User Accounts | HIGH | Account takeover, credential theft |
| System Data | MEDIUM | DoS, resource exhaustion |
| Application Code | MEDIUM | Code injection, abuse |

### Threat Scenarios

#### 1. Unauthorized Document Access
**Threat**: User A views User B's documents

**Current Risk**: ⚠️ **CRITICAL** - No user authentication

**Mitigations**:
- Implement login/authentication
- Filter all queries by `user_id`
- Verify ownership before display
- Log access attempts

```python
# ✗ Bad (vulnerable)
@app.route('/document/<int:id>')
def view_document(id):
    doc = Document.query.get(id)  # Could be anyone's!
    return render_template('view.html', doc=doc)

# ✓ Good (secure)
@app.route('/document/<int:id>')
@login_required
def view_document(id):
    doc = Document.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('view.html', doc=doc)
```

---

#### 2. Cross-Site Request Forgery (CSRF)
**Threat**: Attacker submits malicious form from another site

**Current Risk**: ⚠️ **CRITICAL** - No CSRF protection

**Example Attack**:
```html
<!-- Evil website includes -->
<form action="https://legal-ease.com/upload" method="POST">
    <input name="file" value="malware.pdf">
    <script>document.forms[0].submit();</script>
</form>
<!-- User's logged-in session gets exploited -->
```

**Mitigation**:
```python
# 1. Add Flask-WTF
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# 2. Include token in forms
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    ...
</form>

# 3. Protect routes
@app.route('/upload', methods=['POST'])
@csrf.protect
def upload_file():
    ...
```

---

#### 3. File Upload Exploitation
**Threat**: Attacker uploads malicious file that crashes system

**Current Risk**: ⚠️ **HIGH** - Limited validation

**Attack Types**:
- **ZIP Bomb**: Compressed file explodes on extract
- **Malformed PDF**: Crashes PDF reader
- **Path Traversal**: Filename like `../../etc/passwd`
- **Duplicate Names**: Two uploads overwrite each other

**Mitigations**:
```python
# 1. Validate extension
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
if file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
    return error("Invalid file type")

# 2. Check size
if file.content_length > 16 * 1024 * 1024:  # 16MB
    return error("File too large")

# 3. Randomize filename to prevent conflicts
import uuid
unique_name = f"{uuid.uuid4()}_{secure_filename(file.filename)}"

# 4. Validate MIME type
import magic
mime = magic.from_buffer(file.read(1024), mime=True)
if mime not in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']:
    return error("File type mismatch")

# 5. Isolate in uploads folder
mkdir -p uploads/
# Never serve files directly via filesystem
```

---

#### 4. Brute Force Attack
**Threat**: Attacker tries thousands of passwords to guess account

**Current Risk**: 🟡 **MEDIUM** - Not applicable yet (no auth)

**Mitigation** (After adding auth):
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Max 5 attempts per minute
def login():
    ...
    
# Or implement lock-out after N failures
failed_attempts = {}

def check_login(email, password):
    if failed_attempts.get(email, 0) >= 5:
        log_security_event(f"Account locked: {email}")
        return error("Account temporarily locked")
    
    if not verify_password(email, password):
        failed_attempts[email] = failed_attempts.get(email, 0) + 1
        return error("Invalid credentials")
    
    failed_attempts[email] = 0  # Reset on success
    return success("Logged in")
```

---

#### 5. SQL Injection
**Threat**: Attacker inserts SQL into input to manipulate queries

**Current Risk**: 🟢 **LOW** - Using SQLAlchemy ORM (prevents injection)

**Safe** (ORM with parameterized queries):
```python
# ✓ Safe - SQLAlchemy handles escaping
doc = Document.query.filter_by(user_id=user_id).all()
```

**Unsafe** (raw SQL concatenation):
```python
# ✗ NEVER DO THIS
query = f"SELECT * FROM document WHERE user_id = {user_id}"
db.session.execute(query)  # Vulnerable!
```

**If must use raw SQL**:
```python
# ✓ Use parameterized queries
query = "SELECT * FROM document WHERE user_id = :user_id"
db.session.execute(text(query), {"user_id": user_id})
```

---

#### 6. Session Hijacking
**Threat**: Attacker steals session token from network or browser storage

**Current Risk**: 🟡 **MEDIUM** - Not applicable yet (no sessions)

**Mitigation** (After implementing auth):
```python
# 1. Secure cookies
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  # No cross-site

# 2. Short timeout
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

# 3. Regenerate on login
from flask_login import login_user
session.clear()  # Clear old session
login_user(user)  # Create new session

# 4. Validate user agent
# Detect if user agent changed mid-session (indicates hijacking)
@app.before_request
def validate_session():
    if 'user_agent' not in session:
        session['user_agent'] = request.headers.get('User-Agent')
    elif session['user_agent'] != request.headers.get('User-Agent'):
        session.clear()
        redirect(url_for('login'))  # Force re-login
```

---

#### 7. Data Exposure at Rest
**Threat**: Attacker accesses database and sees sensitive documents

**Current Risk**: 🟡 **HIGH** - Original documents stored unencrypted

**Solution 1: Don't Store Original Text**
```python
# ✓ Better - Only store summary
document = Document(
    filename=filename,
    summary=summary,  # ← Only this
    key_clauses=[...],
    # ✗ Don't store: original_text
)
```

**Solution 2: Encrypt Sensitive Fields**
```python
from cryptography.fernet import Fernet
from flask import current_app

class EncryptedDocument(db.Model):
    original_text = db.Column(db.String, nullable=True)
    
    @staticmethod
    def encrypt_text(text):
        cipher = Fernet(current_app.config['ENCRYPTION_KEY'])
        return cipher.encrypt(text.encode()).decode()
    
    @staticmethod
    def decrypt_text(encrypted_text):
        cipher = Fernet(current_app.config['ENCRYPTION_KEY'])
        return cipher.decrypt(encrypted_text.encode()).decode()
```

**Solution 3: Auto-Delete After Period**
```python
document = Document(
    ...
    expires_at = datetime.utcnow() + timedelta(days=30)  # Delete after 30 days
)

# Cleanup job
def cleanup_expired_documents():
    expired = Document.query.filter(
        Document.expires_at < datetime.utcnow()
    ).all()
    
    for doc in expired:
        db.session.delete(doc)
    db.session.commit()
```

---

#### 8. Denial of Service (DoS)
**Threat**: Attacker floods server with requests, making it unavailable

**Current Risk**: 🟡 **HIGH** - No rate limiting

**Mitigation**:
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

# Rate limit specific endpoints
@app.route('/upload', methods=['POST'])
@limiter.limit("5 per minute")  # Max 5 uploads/minute per IP
def upload_file():
    ...

@app.route('/explain', methods=['POST'])
@limiter.limit("20 per minute")  # Max 20 explanations/minute per IP
def explain_clause():
    ...

# Custom error handler
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded'}), 429
```

---

#### 9. Information Disclosure
**Threat**: Error messages reveal system information (stack traces, paths, software versions)

**Current Risk**: 🟡 **MEDIUM** - Debug mode enabled in development

**Mitigation**:
```python
# 1. Production configuration
app.config['DEBUG'] = False  # Never True in production
app.config['ENV'] = 'production'

# 2. Generic error pages
@app.errorhandler(500)
def internal_error(e):
    logging.error(f"Internal server error: {e}")
    return jsonify({'error': 'An error occurred. Please contact support.'}), 500

# NOT:
return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# 3. Logging sensitive info to file, not user
logging.error(f"Database connection failed: {str(e)}")  # Log only
flash('Database error occurred', 'error')  # User sees vague message
```

---

## Secure Coding Practices

### Input Validation

```python
# Always validate input size
MAX_CLAUSE_LENGTH = 5000
clause = request.form.get('clause_text', '')[:MAX_CLAUSE_LENGTH]

# Always whitelist, never blacklist
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
ext = file.filename.rsplit('.', 1)[1].lower()
if ext not in ALLOWED_EXTENSIONS:
    return error("Invalid file type")

# Validate length
if len(document.summary) > 10000:
    return error("Summary too long")

# Validate email format
import email_validator
try:
    valid = email_validator.validate_email(email)
except email_validator.EmailNotValidError:
    return error("Invalid email format")
```

### Output Encoding

```html
<!-- Always escape user input in templates -->
<!-- ✗ Bad: Could be XSS -->
<p>{{ user_text }}</p>

<!-- ✓ Good: Jinja2 auto-escapes by default -->
<p>{{ user_text | escape }}</p>

<!-- For HTML content, explicitly escape -->
<p>{{ user_html | striptags }}</p>

<!-- For JavaScript, use safe JSON encoding -->
<script>
    var userText = {{ user_text | tojson }};
</script>
```

### Error Handling

```python
# ✓ Good: Specific exception handling
try:
    db.session.commit()
except SQLAlchemyError as e:
    db.session.rollback()
    logging.error(f"Database error: {str(e)}")
    flash('Database error occurred', 'error')
    return redirect(url_for('index'))

# ✗ Bad: Too broad
try:
    db.session.commit()
except:
    flash('Error occurred')
```

### Logging Security Events

```python
def log_security_event(event_type, user_id=None, details=None):
    """Log security-related events for audit trail"""
    log_entry = SecurityLog(
        event_type=event_type,  # login_success, login_failure, permission_denied
        user_id=user_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        details=details,  # Avoid logging passwords
        timestamp=datetime.utcnow()
    )
    db.session.add(log_entry)
    db.session.commit()

# Usage:
log_security_event('failed_login', details={'email': email})
log_security_event('document_accessed', user_id=user.id, details={'doc_id': doc_id})
log_security_event('unauthorized_access_attempt', details={'attempted_doc_id': doc_id})
```

---

## Deployment Security Checklist

- [ ] `FLASK_DEBUG = False` (never True in production)
- [ ] `SESSION_SECRET` is 32+ character random string
- [ ] `DATABASE_URL` uses strong password
- [ ] HTTPS enabled (Render provides free SSL)
- [ ] Database backups configured
- [ ] Error logging enabled (not console, file or service)
- [ ] Security headers configured:
  ```python
  @app.after_request
  def set_security_headers(response):
      response.headers['X-Content-Type-Options'] = 'nosniff'
      response.headers['X-Frame-Options'] = 'DENY'
      response.headers['X-XSS-Protection'] = '1; mode=block'
      response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
      return response
  ```
- [ ] CSRF protection enabled on all forms
- [ ] Rate limiting configured
- [ ] User authentication implemented
- [ ] Authorization checks on all endpoints
- [ ] Secrets not in `.env` (use Render environment UI)
- [ ] Sensitive columns encrypted
- [ ] Regular security audits scheduled

---

## Dependency Security

### Check for Vulnerabilities

```bash
# Install safety
pip install safety

# Check dependencies for known vulnerabilities
safety check -r requirements.txt

# Or use Snyk (free tier available)
pip install snyk
snyk test
```

### Keep Dependencies Updated

```bash
# Show outdated packages
pip list --outdated

# Update specific package
pip install --upgrade flask

# Update all (carefully!)
pip install --upgrade -r requirements.txt
```

### Avoid Suspicious Packages

- Download from PyPI only
- Check package maintainers
- Look for recent commits
- Read security advisories

---

## Incident Response

**If a security breach is discovered**:

1. **Contain**: Immediately disable affected systems
2. **Assess**: Determine scope (what data was accessed, when)
3. **Notify**: Alert users whose data was compromised
4. **Remediate**: Fix the vulnerability
5. **Review**: Post-incident analysis to prevent recurrence
6. **Communicate**: Transparent communication with stakeholders

---

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Common web vulnerabilities
- [Flask Security](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/) - Best practices
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html) - Injection prevention
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/) - Software weaknesses

---

**Last Updated**: Feb 2026  
**Version**: 1.0  
**Reviewed By**: Security Team
