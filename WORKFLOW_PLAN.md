# 📊 Development Workflow & MVP Plan

Strategic roadmap for bringing Legal-Ease from current state to production-ready MVP.

## 🎯 Project Vision

**Goal**: Create a secure, user-friendly AI-powered legal document summarizer that helps students understand complex legal texts.

**MVP Scope**: Core summarization with basic user management and security.

**Success Metrics**:
- App deploys without errors ✓
- Users can upload and get summaries ✓
- Document history is private per user ✓
- No critical security vulnerabilities ✓

## 📅 Sprint Planning

### Phase 1: Critical Fixes (Week 1)
**Objective**: Fix blockers that prevent MVP from running

**Issues to Resolve**:
- [ ] Fix missing `@app.route('/index')` decorator (blocks UI access)
- [ ] Fix `Procfile` gunicorn command (blocks deployment)
- [ ] Add Pillow/pytesseract to requirements.txt (camera feature)
- [ ] Remove hardcoded `SESSION_SECRET` default (security)
- [ ] Fix duplicate HTML footer in index.html (code quality)
- [ ] Implement basic user authentication (privacy)
- [ ] Add user_id filtering to document queries (security)

**Success Criteria**:
- [ ] App starts without errors
- [ ] Home page loads
- [ ] Can upload a test PDF
- [ ] Summary displays on same page
- [ ] Deploy to Render is successful

**Estimated Hours**: 16-20

---

### Phase 2: Security Hardening (Week 2)
**Objective**: Implement essential security controls

**Issues to Resolve**:
- [ ] Add CSRF protection to all forms
- [ ] Input validation on all endpoints
- [ ] Rate limiting (5 requests/min per IP)
- [ ] File upload verification (name randomization)
- [ ] Database query isolation by user
- [ ] Remove original text storage (or add encryption)
- [ ] Add error logging to file (not just console)
- [ ] Session timeout configuration

**Success Criteria**:
- [ ] No CSRF vulnerabilities
- [ ] All inputs validated with length limits
- [ ] Rate limiter prevents abuse
- [ ] Cannot access other users' documents
- [ ] Comprehensive error logging

**Estimated Hours**: 12-16

---

### Phase 3: Stability & Testing (Week 3)
**Objective**: Ensure application is production-ready

**Issues to Resolve**:
- [ ] Database error handling in all routes
- [ ] Graceful degradation for unavailable OCR
- [ ] Handle edge cases (empty documents, corrupted files)
- [ ] Test all routes manually
- [ ] Load testing (can handle 10 concurrent uploads?)
- [ ] Refactor app.py into blueprints
- [ ] Write unit tests for utils functions
- [ ] Document all API endpoints

**Success Criteria**:
- [ ] All manual tests pass
- [ ] Load test shows acceptable performance
- [ ] 80%+ code coverage for critical functions
- [ ] API documentation complete
- [ ] Setup guide tested by new developer

**Estimated Hours**: 14-18

---

### Phase 4: Polish & Launch (Week 4)
**Objective**: Final refinement and production launch

**Issues to Resolve**:
- [ ] Complete Terms of Service page
- [ ] Complete Privacy Policy page
- [ ] Complete Disclaimer page
- [ ] Add user account management (change password, export data)
- [ ] Add document management (delete, re-download summary)
- [ ] Responsive design testing on mobile
- [ ] Performance optimization (cache summaries?)
- [ ] Clean up unused dependencies
- [ ] Prepare deployment runbook

**Success Criteria**:
- [ ] No outstanding bugs in MVP requirements
- [ ] All legal pages content-complete
- [ ] Mobile-friendly interface
- [ ] <3 second load time for summary
- [ ] Deployment process documented

**Estimated Hours**: 12-14

---

## 🏗️ Architecture Evolution

### Current State (Problematic)
```
app.py (330 lines) ← All routes and logic
├── models.py (factory pattern - awkward)
├── utils.py (602 lines - too big)
├── templates/ (3 pages)
└── static/ (CSS, JS, images)
```

### Target State (Clean)
```
app.py (100 lines) ← App factory + config
├── config.py ← Configuration class
├── models.py ← Database models
├── extensions.py ← db, csrf, limiter instances
├── routes/ ← Blueprints
│   ├── auth.py (register, login, logout)
│   ├── documents.py (upload, view, delete)
│   └── api.py (explain, summary)
├── utils/ ← Helper functions
│   ├── text_extraction.py
│   ├── summarization.py
│   └── validation.py
├── static/
├── templates/
└── tests/
    ├── test_routes.py
    ├── test_utils.py
    └── test_models.py
```

## 🔄 User Flow Improvements

### Current Flow (Broken)
```
User
  ↓
? (Cannot access / - returns "is running")
  ↓
Try /index → Not routed
  ↓
??? Cannot use app
```

### Fixed Flow (MVP)
```
User
  ↓
GET / → Home page with upload form
  ↓
Upload document (PDF/DOCX/TXT)
  ↓
POST /upload → Extract text → AI summarize
  ↓
Display summary + key clauses on same page
  ↓
User can /document/<id> to view history
  ↓
User can DELETE /document/<id>
  ↓
User can LOGOUT
```

### Ideal Flow (Post-MVP)
```
User
  ↓
GET / → Landing page (not logged in)
  ↓
Sign up → Create account
  ↓
Login → Dashboard
  ↓
Upload document
  ↓
See summary + clauses
  ↓
Email summary (optional)
  ↓
Export as PDF (optional)
  ↓
Manage documents → Share link (optional)
```

## 📚 Data Model Evolution

### Current
```python
Document
├── filename
├── file_type
├── file_size
├── original_text ← RISKY (entire document stored)
├── summary
├── upload_date
└── processing_time

KeyClause
├── document_id
├── clause_type
├── content
└── explanation

ProcessingLog
├── document_id
├── action
├── status
├── error_message
├── timestamp
└── ip_address
```

### MVP (Secure)
```python
User  # NEW - Required for MVP
├── id
├── email
├── password_hash
├── created_at
└── updated_at

Document (Modified)
├── id
├── user_id ← NEW - Link to user
├── filename
├── file_type
├── file_size
├── summary
├── key_clauses (JSON) ← Instead of separate table
├── upload_date
├── processing_time
├── expires_at ← Optional: auto-delete after 30 days
└── is_deleted ← Soft delete

KeyClause (Keep but reference User)
├── document_id
├── clause_type
├── content
└── explanation

ProcessingLog (With User)
├── id
├── user_id ← NEW
├── document_id
├── action
├── status
├── error_message
├── timestamp
└── ip_address
```

## 🔐 Security Implementation Roadmap

### Week 2 Priority
1. **User Authentication**
   - Flask-Login integration
   - Session management
   - Login/Logout routes
   - Password hashing (werkzeug.security)

2. **Authorization**
   - @login_required decorator
   - User-scoped queries
   - Document ownership verification

3. **CSRF Protection**
   - Flask-WTF integration
   - {{ csrf_token() }} in forms
   - Verify on POST/PUT/DELETE

4. **Input Validation**
   - Length limits on all text inputs
   - File type verification
   - Sanitization of user input

### Week 3-4 Extensions
5. **Data Protection**
   - Session timeout (15 min idle)
   - Secure cookies (HttpOnly, SameSite)
   - Rate limiting
   - Brute force protection

6. **Audit Trail**
   - Log all user actions
   - Track failed login attempts
   - Document access history

## 📦 Dependency Management

### Current Issues
- `torch` and `transformers` listed but not used
- `Pillow` and `pytesseract` commented out but needed
- `pyproject.toml` has 1000+ lines of unused PyTorch index config

### Action Items
```bash
# Week 1
- Uncomment: Pillow, pytesseract in requirements.txt
- Remove: transformers, torch (use Sumy only for MVP)
- Clean up: pyproject.toml (remove PyTorch indices)

# Week 2-3
- Add: Flask-Login, Flask-Limiter, Flask-WTF
- Evaluate: Need Flask-Migrate for schema versioning

# Final
- Audit: Run `pip audit` for security vulnerabilities
```

## 🧪 Testing Strategy

### Unit Tests (Target: Week 3)
```python
# test_utils.py
- test_extract_text_from_txt()
- test_extract_text_from_pdf()
- test_extract_text_from_docx()
- test_summarize_empty_text()
- test_identify_key_clauses()
- test_explain_legal_clause()

# test_models.py
- Test Document creation with user_id
- Test KeyClause relationships
- Test ProcessingLog recording

# test_routes.py
- test_upload_requires_auth()
- test_user_sees_only_own_documents()
- test_rate_limiting_works()
- test_invalid_file_rejected()
```

### Integration Tests (Target: Week 4)
```python
# Full workflow
1. Create user account
2. Login
3. Upload document
4. Verify summary shows
5. Verify can view history
6. Verify cannot access other user's documents
7. Logout
```

### Load Testing (Target: Week 3)
```bash
# Test with concurrent requests
- 10 concurrent uploads
- Expected latency: <5s per request
- Success rate: 100%
```

## 📊 Success Metrics & Milestones

| Milestone | Target Date | Status | Blocker |
|-----------|-------------|--------|---------|
| Phase 1: Critical Fixes | End Week 1 | ❌ Not Started | Route missing |
| Phase 2: Security | End Week 2 | ❌ Not Started | Auth not implemented |
| Phase 3: Testing | End Week 3 | ❌ Not Started | Needs tests |
| Phase 4: Launch | End Week 4 | ❌ Not Started | MVP complete |
| **Production Deployment** | **End Week 4** | ❌ Not Started | All phases pass |

## 💾 Branching Strategy

```
main (stable, production-ready)
├── hotfix/urgent-bug (for critical fixes)
│   └── PR → main
└── develop (integration branch)
    ├── feature/user-auth
    │   └── PR → develop
    ├── feature/csrf-protection
    │   └── PR → develop
    ├── feature/rate-limiting
    │   └── PR → develop
    └── fix/route-missing
        └── PR → develop → main
```

**Merge Strategy**:
- All PRs require code review
- All tests must pass
- All security checks must pass
- 1 approval minimum before merge

## 🚀 Deployment Checklist

Before going live:

- [ ] All critical phase bugs fixed
- [ ] All security measures implemented
- [ ] Database migrations tested
- [ ] Load testing passed
- [ ] Manual test suite passed
- [ ] Error logging working
- [ ] Monitoring configured
- [ ] Rollback plan documented
- [ ] Support runbook created
- [ ] Analytics configured

## 📞 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Route not accessible | HIGH | CRITICAL | Fix 1st thing |
| Deployment fails | HIGH | CRITICAL | Test Procfile locally |
| Security vulnerability | HIGH | CRITICAL | Security audit week 2 |
| Database performance | MEDIUM | HIGH | Use connection pooling |
| OCR not available | LOW | MEDIUM | Graceful fallback |
| File upload bomb | MEDIUM | HIGH | Strict size/rate limits |

## 📚 Documentation Deliverables

- [ ] SETUP_ENV.md (setup instructions)
- [ ] WORKFLOW_PLAN.md (this file)
- [ ] API_DOCUMENTATION.md (endpoint specs)
- [ ] ARCHITECTURE.md (system design)
- [ ] SECURITY_POLICY.md (security guidelines)
- [ ] CONTRIBUTING.md (contribution guidelines)
- [ ] Code comments (docstrings for functions)
- [ ] Deployment runbook (ops procedures)

---

**Last Updated**: Feb 2026  
**Status**: Planning Phase  
**Maintainer**: Development Team  
**Next Review**: Start of Week 1 Sprint
