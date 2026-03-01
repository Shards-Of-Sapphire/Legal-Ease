# 📝 CHANGELOG

All notable changes to Legal-Ease will be documented in this file. 

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project aims to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - MVP Development

### Planned (Week 1)
- [ ] Fix missing route decorator on `/index`
- [ ] Fix Procfile gunicorn command for deployment
- [ ] Add user authentication system
- [ ] Add document ownership filtering
- [ ] Remove hardcoded SESSION_SECRET default
- [ ] Fix duplicate HTML footer
- [ ] Update requirements.txt with OCR dependencies

### Planned (Week 2)
- [ ] Add CSRF protection to all forms
- [ ] Implement Flask-WTF for form security
- [ ] Add rate limiting (Flask-Limiter)
- [ ] Input validation on all endpoints
- [ ] Database error handling improvements
- [ ] Document deletion endpoint
- [ ] User account management routes

### Planned (Week 3)
- [ ] Refactor app.py into blueprints
- [ ] Write unit tests (target 80% coverage)
- [ ] Add Flask-Migrate for database migrations
- [ ] File upload verification (randomize filenames)
- [ ] Add logging to file (not just console)
- [ ] Session timeout configuration
- [ ] Error logging and monitoring

### Planned (Week 4)
- [ ] Complete Terms of Service page
- [ ] Complete Privacy Policy page
- [ ] Complete Disclaimer page
- [ ] Load testing and optimization
- [ ] Clean up unused dependencies (remove transformers)
- [ ] Performance benchmarking
- [ ] Security audit checklist
- [ ] Documentation review and finalization

## [0.1.0-alpha] - Initial Development

### Added
- Core Flask application structure
- Document upload endpoint (`POST /upload`)
- PDF, DOCX, TXT text extraction
- AI-powered document summarization using Sumy LSA algorithm
- Key clause identification (8 clause types)
- Legal clause explanation module
- Document history viewing (`GET /history`)
- Camera capture with Tesseract OCR (experimental)
- Dark theme UI with Bootstrap 5
- Modal for clause explanations
- Drag-and-drop file upload with client-side validation
- File size validation (16MB limit)
- File type validation (PDF, DOCX, TXT only)
- Database models for Document, KeyClause, ProcessingLog
- SQLAlchemy ORM integration
- SQLite (development) / PostgreSQL (production) support
- Legal pages: Terms, Privacy, Disclaimer (incomplete)
- Basic error handling and user feedback

### Known Issues
- [ ] Route decorator missing on `index()` function - blocks UI access
- [ ] Procfile has wrong gunicorn command - prevents deployment
- [ ] No user authentication - all documents visible to everyone
- [ ] No CSRF protection - vulnerable to cross-site attacks
- [ ] Original documents stored in plaintext - privacy risk
- [ ] No rate limiting - vulnerable to DoS
- [ ] File upload names can conflict - overwrites possible
- [ ] OCR dependencies commented out in requirements
- [ ] No tests written yet - untested functionality
- [ ] app.py is 330 lines - needs refactoring into blueprints
- [ ] Inconsistent error handling - some errors not caught

### Limitations
- Single-server deployment only
- No user authentication
- No async processing (blocks on large files)
- Limited to Sumy summarization (no advanced transformers yet)
- No caching of results
- No full-text search of documents
- No document sharing/collaboration
- No API rate limiting

---

## Version Information

### Current Status: MVP Phase (Week 1-4)
- Target: Production-ready basic functionality
- Priority: Security, reliability, usability
- Testing: Manual before MVP, automated after Week 2

### Planned Milestones

**v0.1.0-alpha** (Current)
- Initial development with critical bugs

**v0.1.0-beta** (Week 1-2)
- Critical fixes + security implementation
- Basic authentication
- CSRF protection
- Input validation

**v0.1.0-rc1** (Week 3)
- Unit tests passing
- Performance optimized
- Error handling comprehensive
- Security audit complete

**v1.0.0** (Week 4)
- Production launch
- MVP requirements met
- Documentation complete
- Deployment on Render successful

**v1.1.0** (Future)
- User onboarding/tutorials
- Document sharing
- Email summaries
- Export to PDF

**v2.0.0** (Future)
- Advanced transformers for better summaries
- Full-text search
- Batch processing
- API rate limiting per user per month
- Team collaboration features

---

## Changes by Category

### Security Enhancements
- [Unreleased] Add CSRF protection
- [Unreleased] Add authentication
- [Unreleased] Add rate limiting
- [Unreleased] Encrypt sensitive fields

### Bug Fixes
- [Unreleased] Fix missing `/index` route
- [Unreleased] Fix Procfile deployment command
- [Unreleased] Fix OCR dependencies in requirements.txt
- [Unreleased] Fix duplicate HTML footer

### Performance Improvements
- [Unreleased] Add result caching
- [Unreleased] Optimize text extraction

### Features
- [0.1.0-alpha] Document upload & summarization
- [0.1.0-alpha] Key clause identification
- [0.1.0-alpha] Clause explanation
- [0.1.0-alpha] Document history
- [0.1.0-alpha] Camera capture with OCR

### Documentation
- [Unreleased] Add API documentation
- [Unreleased] Add setup guide
- [Unreleased] Add security policy
- [Unreleased] Add architecture documentation
- [Unreleased] Add contributing guide

---

## Upgrading

### From 0.1.0-alpha to 0.1.0-beta

1. **Database Migration**:
   ```bash
   # Add user_id column to existing tables
   # (Use Flask-Migrate when available)
   python scripts/migrate_to_user_auth.py
   ```

2. **Configuration Updates**:
   ```bash
   # Copy new env variables
   cp .env.example .env
   # Edit with your settings
   ```

3. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install Flask-WTF Flask-Limiter
   ```

4. **Deployment**:
   ```bash
   # Update Procfile
   git push origin main
   # Render auto-deploys
   ```

---

## Contributors

- **Founders**: Shaik Zayed Saleem, Roushna Khatoon
- **Organization**: Sapphire (Student-led innovation group)
- **Institution**: Muffakham Jah College of Engineering and Technology

### Community Contributors
(Will be updated as contributions are made)

---

## License

This project is licensed under the MIT License - see LICENSE file for details.

---

**Last Updated**: Feb 2026  
**Version**: 0.1.0-alpha  
**Next Release**: v0.1.0-beta (Week 1-2)
