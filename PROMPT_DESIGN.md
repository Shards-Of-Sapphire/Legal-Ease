# 🤖 Prompt Design & AI Assistant Guidelines

This document defines how to effectively communicate with AI assistants (like Claude) and LLMs when working on Legal-Ease. Use these patterns for consistent, productive interactions.

## Project Context

**Project Name**: Legal-Ease  
**Organization**: Shards-Of-Sapphire (Student-led innovation group)  
**Purpose**: AI-powered legal document summarization  
**Stack**: Python Flask, SQLAlchemy, HuggingFace Transformers, Sumy NLP

## 🎯 Key Project Goals

1. **MVP Phase**: Basic functionality with essential security
2. **Core Feature**: Summarize legal documents (PDF, DOCX, TXT)
3. **AI Capabilities**: Extract key clauses and explain legal terms
4. **User Focus**: Students and non-lawyers needing document clarity

## 📋 Critical Constraints

### Architecture Constraints
- **Single Page App**: Results display on same page as upload
- **Database**: SQLAlchemy with PostgreSQL (Render) or SQLite (local dev)
- **No ML Training**: Use pre-trained models only (Transformers, Sumy)
- **Stateless Deployment**: Ready for Gunicorn on Render

### Security Constraints
- **No User Auth Yet**: MVP should have simple auth (session-based)
- **No Secrets in Code**: All config from environment variables
- **Privacy First**: Original documents should NOT be stored long-term
- **CSRF Protection**: Required for all forms

### Performance Constraints
- **Max File Size**: 16MB (hard limit)
- **Max Processing Time**: 30 seconds per document
- **Max Summary Output**: Should fit on one page

## 🔴 Red Flags (Halt & Ask)

If you encounter these issues, **stop and ask the human before proceeding**:

1. **Schema Changes**: Any database model modifications
2. **API Changes**: Modifying request/response contracts of endpoints
3. **Auth Implementation**: Adding user authentication (needs discussion)
4. **Dependency Additions**: New packages > 100MB or production dependencies
5. **Breaking Changes**: Code that affects existing deployed functionality

## ✅ When to Make Decisions Independently

- **Bug Fixes**: Fix syntax errors, logical bugs without asking
- **Code Quality**: Refactoring for readability, PEP8 compliance
- **Documentation**: Adding/updating docstrings and comments
- **Test Addition**: Adding tests for existing functionality
- **Minor Config**: Adjusting timeouts, batch sizes, thresholds

## 📝 How to Write Effective Prompts for AI

### Format for Code Reviews
```
I need a code review of [FILE_PATH] focusing on:
- Security issues (authentication, input validation)
- Performance bottlenecks
- Python best practices

List issues as: 
1. CRITICAL: [issue] - [fix]
2. HIGH: [issue] - [fix]
```

### Format for Implementations
```
Please implement [FEATURE] in [FILE]:
- **What**: [Brief description]
- **Why**: [Business reason]
- **Where**: [File/function location]
- **Constraints**: [Limitations to respect]
- **Testing**: [How to verify]
```

### Format for Debugging
```
Error: [ERROR MESSAGE]
Location: [FILE:LINE]
Current behavior: [WHAT HAPPENS]
Expected behavior: [WHAT SHOULD HAPPEN]
Context: [RECENT CHANGES OR SETUP INFO]
```

### Format for Architecture Questions
```
Question: [WHAT YOU WANT TO KNOW]
Current: [HOW IT WORKS NOW]
Problem: [WHY IT'S NOT RIGHT]
Options: [2-3 possible solutions]
Preference: [WHAT YOU LEAN TOWARD]
```

## 🗂️ File Organization Rules for AI

When asking for changes, reference files consistently:

- **Backend Code**: `app.py`, `utils.py`, `models.py` (always at `/workspaces/Legal-Ease/`)
- **Templates**: Prefix with `templates/` (e.g., `templates/index.html`)
- **Static Assets**: Prefix with `static/` (e.g., `static/js/script.js`)
- **Configuration**: Prefix with root (e.g., `Procfile`, `requirements.txt`)

## 🔧 Common Task Patterns

### Pattern 1: Bug Fix Request
```
BUG: [Route/Function] is returning [ERROR]

Investigation:
- Error message: [EXACT MESSAGE]
- Stack trace: [RELEVANT LINES]
- Reproduction: [STEPS TO REPRODUCE]

Expected resolution: Fix [FILE] line [X], changing [OLD] to [NEW]
```

### Pattern 2: Security Audit
```
SECURITY: Audit [COMPONENT] for [VULNERABILITY TYPE]

Scope:
- File: [FILE]
- Function: [FUNCTION_NAME]
- Risk level: [CRITICAL/HIGH/MEDIUM]

Report should include:
1. Vulnerability description
2. Potential impact
3. Code location
4. Recommended fix
```

### Pattern 3: Performance Optimization
```
PERFORMANCE: Optimize [OPERATION/ROUTE]

Current state:
- Current time: [MS/SECONDS]
- Bottleneck: [WHERE IT'S SLOW]
- Usage frequency: [HOW OFTEN CALLED]

Target:
- Target time: [MS/SECONDS]
- Acceptable trade-off: [WHAT WE'RE WILLING TO SACRIFICE]
```

### Pattern 4: Feature Addition
```
FEATURE: Add [FEATURE_NAME]

Requirements:
- User can: [ACTION]
- System should: [BEHAVIOR]
- Constraint: [LIMITATION]

Acceptance criteria:
1. [MEASURABLE CRITERION]
2. [MEASURABLE CRITERION]
3. [MEASURABLE CRITERION]
```

## 📊 Code Style Guidelines for AI

### Python Style
- Use PEP 8 guidelines
- Type hints where applicable (Python 3.11+)
- Docstrings for all functions and classes
- Error handling with specific exceptions, not bare `except`

### Naming Conventions
- **Routes**: kebab-case (e.g., `/upload-file`, `/explain-clause`)
- **Functions**: snake_case (e.g., `extract_text_from_pdf()`)
- **Classes**: PascalCase (e.g., `Document`, `ProcessingLog`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_FILE_SIZE`)

### HTML/CSS
- Use Bootstrap 5.3 classes (dark theme)
- Font Awesome 6.0 for icons
- Avoid inline styles (use external CSS)
- Semantic HTML elements

### JavaScript
- Use vanilla JS (no jQuery)
- Event delegation for dynamic elements
- Error handling with try/catch
- User feedback with alerts or toast notifications

## 🧪 Testing Expectations

For any code change, prefer:

```python
# Good: Specific exception handling
try:
    result = process_document(file)
except ValueError as e:
    logging.error(f"Invalid document format: {e}")
    return jsonify({'error': str(e)}), 400

# Bad: Bare except
try:
    result = process_document(file)
except:
    return "Error"
```

## 📱 API Response Format

All JSON responses should follow:

```json
{
  "success": true,
  "data": {
    "key": "value"
  },
  "message": "Optional message to user"
}
```

Or on error:

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE"
}
```

## 🚀 Deployment Expectations

Code should be deployable to:
- **Local Development**: `python main.py` (development server)
- **Production**: `gunicorn app:app` (Render platform)
- **Database**: PostgreSQL (production) or SQLite (development)

Never hardcode:
- API keys
- Database URLs
- Session secrets
- File paths

Always use:
- Environment variables
- Configuration classes
- Conditional imports for optional features

## 🎓 Learning Resources for AI Context

- **Flask Framework**: [Flask Documentation](https://flask.palletsprojects.com/)
- **SQLAlchemy ORM**: [SQLAlchemy Guide](https://docs.sqlalchemy.org/)
- **NLP Models**: Project uses Sumy (Extractive) and Transformers (Potential)
- **Legal Document Processing**: Text extraction from PDF, DOCX, TXT formats
- **Deployment**: Render platform with Gunicorn WSGI

## 📞 Escalation Path

If an AI assistant encounters:
1. **Ambiguous Requirements**: Ask clarifying questions
2. **Conflicting Constraints**: State both options, ask human to choose
3. **Unknown Territory**: Research the topic, propose solution, ask for approval
4. **External Dependencies**: Note that package affects build size/complexity

## 📋 Checklist for AI Before Coding

- [ ] I understand the business requirement
- [ ] I know which files need modification
- [ ] I've identified security implications
- [ ] I've considered backward compatibility
- [ ] I've noted any new dependencies
- [ ] I've planned error handling
- [ ] I've considered deployment impact
- [ ] I'm ready to explain the changes clearly

---

**Last Updated**: Feb 2026  
**Maintained By**: Development Team  
**Version**: 1.0
