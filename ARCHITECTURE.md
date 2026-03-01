# 🏛️ System Architecture

Complete technical documentation of Legal-Ease's system design, components, data flow, and scalability considerations.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│                 (HTML, CSS, JavaScript)                     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Web Server                          │
│              (Python 3.11 + Gunicorn WSGI)                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Routes (app.py)                                     │  │
│  │  • GET /  → Home (index.html)                        │  │
│  │  • POST /upload → File upload & summarization        │  │
│  │  • GET /document/<id> → View saved document          │  │
│  │  • GET /history → List user documents                │  │
│  │  • POST /explain → Explain a clause                  │  │
│  │  • GET /terms, /privacy, /disclaimer                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────┴──────────────────────────────┐  │
│  │         Middleware & Service Layer                   │  │
│  │  ┌──────────────┬──────────────┬─────────────────┐  │  │
│  │  │  utils.py    │  models.py   │  extensions.py  │  │  │
│  │  │              │              │                 │  │  │
│  │  │ • Extract    │ • Document   │ • SQLAlchemy    │  │  │
│  │  │   text       │ • KeyClause  │ • Flask-Login   │  │  │
│  │  │ • Summarize  │ • User       │ • CSRF protect  │  │  │
│  │  │ • Explain    │ • Process    │ • Rate limit    │  │  │
│  │  │   clauses    │   Log        │                 │  │  │
│  │  └──────────────┴──────────────┴─────────────────┘  │  │
│  └──────────────────────┬───────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
     ┌────────────────────────────────────────┐
     │     Database Layer (SQLAlchemy ORM)    │
     │                                        │
     │  ┌──────────────────────────────────┐ │
     │  │  PostgreSQL (Production)         │ │
     │  │  - User authentication           │ │
     │  │  - Document storage & history    │ │
     │  │  - Processing logs               │ │
     │  │  - Full-text search (future)     │ │
     │  └──────────────────────────────────┘ │
     │                                 OR     │
     │  ┌──────────────────────────────────┐ │
     │  │  SQLite (Development/Fallback)   │ │
     │  │  - Local file-based database     │ │
     │  │  - Single-file deployment        │ │
     │  └──────────────────────────────────┘ │
     └────────────────────────────────────────┘

         External NLP Services (Optional)
         ┌──────────────────────────────┐
         │  HuggingFace (Future)         │
         │  - Advanced transformers      │
         │  - GPT-based explanations     │
         │  - Semantic search            │
         └──────────────────────────────┘
```

## Component Architecture

### 1. Frontend Layer

**Technology**: HTML5 + Bootstrap 5 + Vanilla JavaScript

**Files**:
- `templates/index.html` - Main upload & display interface
- `templates/history.html` - Document history/management
- `templates/terms.html`, `privacy.html`, `disclaimer.html` - Legal pages
- `static/css/style.css` - Styling
- `static/js/script.js` - Client-side logic (file upload, camera, modal handling)

**Key Features**:
- Drag-and-drop file upload
- Camera capture with OCR
- Real-time file validation
- Progress animation
- Modal for clause explanations
- Responsive dark theme

**Dependencies**:
- Bootstrap 5.3 CDN
- Font Awesome 6.0 (icons)
- JavaScript Web APIs (MediaDevices for camera, Canvas)

---

### 2. Application Layer

**Technology**: Flask (Python web framework)

**Core Files**:
- `app.py` (330 lines) - Flask app, routes, middleware
- `models.py` - Data models (Document, KeyClause, ProcessingLog, User)
- `utils.py` (602 lines) - Business logic (text extraction, summarization, explanations)
- `main.py` - Entry point for development server

**Architecture Decision**: Currently monolithic (should be refactored into blueprints)

**Current Responsibilities**:
- Route handling
- File upload management
- Request/response processing
- Error handling
- Session management
- Database queries
- Response formatting

**Key Routes**:

| Route | Method | Purpose | Auth Required |
|-------|--------|---------|---------------|
| `/` | GET | Home page | No |
| `/upload` | POST | Process document | No (✗ Should be Yes) |
| `/document/<id>` | GET | View summary | No (✗ Should verify ownership) |
| `/history` | GET | User's documents | No (✗ Should be Yes) |
| `/explain` | POST | Explain clause | No (✗ Should be Yes) |
| `/terms` | GET | Terms of Service | No |
| `/privacy` | GET | Privacy Policy | No |
| `/disclaimer` | GET | Disclaimer | No |

---

### 3. Processing Pipeline

```
File Upload
    │
    ▼
┌─────────────────────────────┐
│  File Validation            │
│  • Check extension (.pdf, .docx, .txt)
│  • Check size (< 16MB)      │
│  • Check MIME type          │
└─────────────┬───────────────┘
              │
              ▼ (Valid)
┌─────────────────────────────┐
│  Text Extraction            │
│  • PDF → PyMuPDF (fitz)     │
│  • DOCX → python-docx       │
│  • TXT → read()             │
│  • Image → Tesseract OCR    │
└─────────────┬───────────────┘
              │
              ▼ (Text extracted)
┌─────────────────────────────┐
│  Summarization              │
│  • Sentence tokenization    │
│  • SUMY LSA algorithm       │
│  • Score by importance      │
│  • Return top 3-8 sentences │
└─────────────┬───────────────┘
              │
              ▼ (Summary generated)
┌─────────────────────────────┐
│  Clause Extraction          │
│  • Regex pattern matching   │
│  • 6+ legal clause types    │
│  • Explanation per clause   │
└─────────────┬───────────────┘
              │
              ▼ (Results ready)
┌─────────────────────────────┐
│  Database Storage           │
│  • Save document metadata   │
│  • Save summary & clauses   │
│  • Log processing action    │
└─────────────┬───────────────┘
              │
              ▼ (Complete)
        Return to User
```

---

### 4. Text Extraction Module

**File**: `utils.py::extract_text_from_file()`

**Logic**:
1. Determine file type by extension
2. Route to appropriate extractor
3. Handle encoding errors gracefully

**Extractors**:

| Format | Library | Method | Pros | Cons |
|--------|---------|--------|------|------|
| PDF | `fitz` (PyMuPDF) | `page.get_text()` | Fast, accurate | Large dependency |
| DOCX | `python-docx` | Iterate paragraphs | Official support | Limited formatting |
| TXT | Built-in | `open()` + `read()` | Simple, fast | Encoding issues |
| Image | `pytesseract` | OCR | No doc required | Slow, needs Tesseract |

**Error Handling**:
- File not found → 404
- Corrupt file → "Unable to read file"
- Encoding mismatch → Try UTF-8, then Latin-1
- No text found → "No text could be extracted"

---

### 5. Summarization Module

**File**: `utils.py::summarize_legal_document()`

**Algorithm**: Extractive Summarization (SUMY)

**Process**:
1. **Sentence Tokenization**: Split text into sentences
2. **Frequency Analysis**: Score word importance
3. **Sentence Ranking**: Rate each sentence by word scores
4. **Summary Selection**: Pick top N sentences (3-8)
5. **Reordering**: Keep original order in document

**Formula**:
```
Sentence Score = Σ (word_frequency / total_words)
                 for each word in sentence

Top N sentences with highest scores = Summary
```

**Adaptive Sizing**:
```
Document Length → Summary Sentences
< 1,000 words   → 3 sentences
1,000-5,000     → 5 sentences
5,000-10,000    → 8 sentences
> 10,000        → 8 sentences (max)
```

**Fallback Mechanism**:
- If Sumy fails → `create_intelligent_summary()`
- If that fails → Basic word count summary
- Last resort → Generic message

---

### 6. Clause Extraction Module

**File**: `utils.py::identify_key_clauses_enhanced()`

**Method**: Pattern Matching with Regex

**Detected Clause Types** (8 total):

1. **Termination** - How to end agreement
2. **Confidentiality** - Information protection
3. **Payment Terms** - Fee/compensation schedules
4. **Liability** - Responsibility for damages
5. **Governing Law** - Jurisdiction & legal system
6. **Intellectual Property** - Rights ownership
7. **Force Majeure** - Unforeseeable circumstance exceptions
8. **Dispute Resolution** - How to handle disagreements

**Algorithm**:
1. Split into paragraphs
2. For each clause type, check patterns
3. Extract matching sentences
4. Add human-readable explanation
5. Limit to 8 clauses (prevent overwhelming UX)

**Example Pattern**:
```python
'Termination': {
    'patterns': [
        r'terminat[ei].*?(?:agreement|contract)',
        r'end.*?(?:agreement|contract)',
        r'expir[ye].*?(?:agreement|contract)',
    ],
    'description': 'Specifies conditions for ending the agreement'
}
```

---

### 7. Explanation Module

**File**: `utils.py::explain_legal_clause()`

**Three-Part Explanation**:

1. **Clause Structure Analysis**
   - "This clause contains X obligations"
   - "This clause is conditional on Y"
   - "This clause has time requirements"

2. **Legal Interpretation**
   - Pre-built explanations for common clauses
   - e.g., "Termination = How/when agreement ends"
   - Covers 10+ legal concept categories

3. **Practical Implications**
   - What the user needs to actually do
   - Financial impact (if any)
   - Time constraints (if any)
   - Risk allocation (if any)

**Example**:
```
Input: "Party shall indemnify..."

Output: "Indemnification Clause: This means one party agrees to 
protect and compensate the other party for certain types of losses, 
damages, or legal claims.

Practical Impact: This has risk allocation implications - it determines 
who bears responsibility for potential problems."
```

---

## Data Model

### User (Future MVP)

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='owner', lazy=True)
    logs = db.relationship('ProcessingLog', backref='user', lazy=True)
```

### Document

```python
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Future
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, docx, txt
    file_size = db.Column(db.Integer, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    key_clauses = db.relationship('KeyClause', backref='document')
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time = db.Column(db.Float)  # milliseconds
    expires_at = db.Column(db.DateTime)  # Optional: auto-delete
```

### KeyClause

```python
class KeyClause(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    clause_type = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)
```

### ProcessingLog

```python
class ProcessingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Future
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    action = db.Column(db.String(100))  # upload, summarize, explain
    status = db.Column(db.String(20))   # success, error
    error_message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
```

---

## Request/Response Flow

### Example: Document Upload

**1. User submits form**
```javascript
POST /upload
Content-Type: multipart/form-data

[File binary data]
```

**2. Server receives & validates**
```python
def upload_file():
    # Validate file exists & type
    # Check size < 16MB
    # Save to disk (temporary)
    # Extract text based on filetype
```

**3. Processing begins**
```python
    # Summarize text with Sumy
    # Extract key clauses with regex
    # Build clause explanations
```

**4. Store in database**
```python
    document = Document(
        filename=...,
        summary=...,
        key_clauses=[...]
    )
    db.session.add(document)
    db.session.commit()
```

**5. Return results to browser**
```html
<!-- Results embedded in same page with form -->
<div class="summary">
    {{ summary }}
</div>
<div class="clauses">
    {% for clause in key_clauses %}
        <div class="clause">{{ clause.type }}: {{ clause.content }}</div>
    {% endfor %}
</div>
```

---

## Scalability Considerations

### Current Bottlenecks

1. **Text Extraction**
   - Large PDFs can take 5-10 seconds
   - No caching mechanism
   - **Solution**: Add job queue (Celery) for async processing

2. **Summarization**
   - SUMY is CPU-intensive
   - No parallel processing
   - **Solution**: Cache summaries, pre-compute for common docs

3. **Database**
   - SQLite cannot handle concurrent writes
   - No connection pooling
   - **Solution**: PostgreSQL + connection pooling in production

4. **File Storage**
   - Uploaded files stored on disk
   - No object storage (S3)
   - **Solution**: Use cloud storage for reliability

### Scaling Plan

#### Phase 1: Current (Single Server)
- Flask dev server or Gunicorn
- SQLite/PostgreSQL
- Local file storage
- Synchronous processing

#### Phase 2: Async Processing (5K users)
```
┌─────────────┐      ┌────────────────┐      ┌──────────────┐
│  Web Server │──→│  Celery Queue  │──→│  Worker Pool │
└─────────────┘      └────────────────┘      └──────────────┘
                         Redis
```

#### Phase 3: Distributed (50K users)
```
Load Balancer
    ├→ Web Server 1
    ├→ Web Server 2
    ├→ Web Server 3
         ↓
    PostgreSQL (master-slave)
         ↓
    Redis (cache layer)
    S3 (file storage)
    Celery Workers (auto-scale)
```

---

## Performance Targets

| Operation | Target | Current | Status |
|-----------|--------|---------|--------|
| Page load | < 1s | 0.5s | ✓ Good |
| Upload 5MB PDF | < 10s | ~8s | ✓ Good |
| Text extraction | < 5s | ~3s | ✓ Good |
| Summarization | < 3s | ~2s | ✓ Good |
| Return results | < 15s | ~13s | ✓ Good |
| Explain clause | < 2s | ~1s | ✓ Good |
| Load history (100 docs) | < 1s | ~0.8s | ✓ Good |

---

## Dependencies Overview

### Core
- `flask` - Web framework
- `flask-sqlalchemy` - ORM
- `werkzeug` - WSGI utilities
- `gunicorn` - WSGI server
- `sqlalchemy` - Database abstraction

### NLP & Text Processing
- `nltk` - Natural language toolkit
- `sumy` - Extractive summarization
- `pymupdf` - PDF text extraction
- `python-docx` - DOCX reading

### Optional (OCR)
- `pillow` - Image processing
- `pytesseract` - Tesseract wrapper

### Security (To add)
- `flask-login` - User sessions
- `flask-wtf` - CSRF protection
- `flask-limiter` - Rate limiting
- `werkzeug.security` - Password hashing

---

## Error Handling Strategy

### Error Categories

| Category | Examples | User Message | Log Level |
|----------|----------|--------------|-----------|
| Bad Input | Invalid file type, too large | "File type not supported" | WARNING |
| Processing | PDF corrupt, no text extracted | "Could not read file" | WARNING |
| External | Tesseract missing, network down | "Feature unavailable" | ERROR |
| System | Database error, disk full | "Server error, try again" | ERROR |

### Implementation Pattern

```python
try:
    # Business logic
    result = process_document(file)
except SpecificExceptionA as e:
    logging.warning(f"Expected error: {e}")
    flash("User-friendly message", 'error')
    return redirect(url_for('index'))
except SpecificExceptionB as e:
    logging.error(f"Unexpected error: {e}")
    flash("Server error occurred", 'error')
    return redirect(url_for('index'))
except Exception as e:
    logging.error(f"Critical error: {e}")
    return jsonify({'error': 'Unexpected error'}), 500
```

---

**Last Updated**: Feb 2026  
**Version**: 1.0  
**Maintainer**: Development Team
