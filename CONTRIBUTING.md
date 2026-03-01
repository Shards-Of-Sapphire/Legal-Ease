# 🤝 Contributing Guide

How to contribute to Legal-Ease - code standards, workflow, testing, and review process.

## Welcome Contributors! 👋

We're excited you want to help make Legal-Ease better. Whether you're fixing bugs, adding features, or improving documentation, your contribution matters.

**Legal-Ease is built by students, for students** - so we value clear communication, patience, and collaborative growth.

---

## Getting Started

### 1. Fork & Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/Legal-Ease.git
cd Legal-Ease

# Add upstream for syncing
git remote add upstream https://github.com/Shards-Of-Sapphire/Legal-Ease.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run setup script (future)
# bash scripts/setup.sh
```

### 3. Create Feature Branch

```bash
# Update main
git checkout main
git pull upstream main

# Create branch (use clear naming)
git checkout -b feature/your-feature-name
# OR for bugs:
git checkout -b fix/bug-description
```

---

## Code Style & Standards

### Python Style Guide (PEP 8)

**File Structure**:
```python
# 1. Imports (stdlib, then third-party, then local)
import os
import logging
from datetime import datetime

import flask
from flask_sqlalchemy import SQLAlchemy

from models import Document
from utils import extract_text_from_pdf

# 2. Constants
MAX_FILE_SIZE = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# 3. Classes
class MyClass:
    pass

# 4. Functions
def my_function():
    pass

# 5. Main guard
if __name__ == '__main__':
    app.run()
```

**Naming Conventions**:
- `ClassName` - Classes (PascalCase)
- `function_name()` - Functions (snake_case)
- `variable_name` - Variables (snake_case)
- `CONSTANT_NAME` - Constants (UPPER_SNAKE_CASE)
- `_private_method()` - Private methods (leading underscore)

**Line Length**: Maximum 100 characters

**Docstrings**: Required for all functions and classes

```python
def extract_text_from_pdf(filepath):
    """Extract text from a PDF file.
    
    Args:
        filepath (str): Path to the PDF file
        
    Returns:
        str: Extracted text from all pages
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a valid PDF
        
    Example:
        >>> text = extract_text_from_pdf('contract.pdf')
        >>> print(text[:50])  # First 50 chars
    """
    # Implementation
    pass
```

**Type Hints** (Python 3.11+):

```python
from typing import Optional, List

def summarize_document(text: str, max_sentences: int = 5) -> str:
    """Summarize a document."""
    pass

def process_files(files: List[str]) -> Optional[dict]:
    """Process multiple files."""
    pass
```

**Error Handling**:

```python
# ✓ Good - Specific exception handling
try:
    document = Document.query.get_or_404(doc_id)
except NotFound as e:
    logging.warning(f"Document not found: {doc_id}")
    flash('Document not found', 'error')
    return redirect(url_for('index'))
except SQLAlchemyError as e:
    logging.error(f"Database error: {str(e)}")
    flash('Database error occurred', 'error')
    return redirect(url_for('index'))

# ✗ Bad - Too broad, hides errors
try:
    process_data()
except:
    print("Error")
```

**Comments**:

```python
# ✓ Good - Explains WHY, not WHAT
# Use LSA summarizer instead of TF-IDF because legal documents
# have lots of repetitive domain-specific terms that skew TF-IDF
summarizer = LsaSummarizer(stemmer)

# ✗ Bad - Obvious in code
# Set x to 5
x = 5

# These are good:
# TODO: Implement user authentication
# FIXME: PDF extraction fails on encrypted documents
# NOTE: This is a workaround for Sumy's NLTK requirement
# HACK: Temporary solution until Flask-Login is integrated
```

### HTML/CSS Style

**HTML**:
```html
<!-- Use semantic elements -->
<main>
  <section id="upload">
    <h1>Upload Document</h1>
    <form method="POST" action="/upload">
      {{ csrf_token() }}
      <input type="file" name="file" required>
    </form>
  </section>
</main>

<!-- Bootstrap 5 classes for layout -->
<div class="container mt-4">
  <div class="row justify-content-center">
    <div class="col-lg-8">
      <!-- Content -->
    </div>
  </div>
</div>
```

**CSS**:
```css
/* Use external stylesheets, not inline styles */
/* Prefer CSS variables for theming */
:root {
  --primary-color: #007bff;
  --danger-color: #dc3545;
  --spacing-unit: 1rem;
}

/* Use BEM naming (Block Element Modifier) */
.upload-form { }
.upload-form__input { }
.upload-form__button { }
.upload-form__button--disabled { }
```

**No inline styles**:
```html
<!-- ✗ Bad -->
<div style="display: flex; gap: 10px;">

<!-- ✓ Good -->
<div class="flex-container">
  <!-- CSS in style.css -->
</div>
```

### JavaScript Style

```javascript
// Use const/let, not var
const MAX_FILE_SIZE = 16 * 1024 * 1024;
let uploadProgress = 0;

// Use arrow functions for callbacks
document.addEventListener('click', (e) => {
  handleClick(e);
});

// Use template literals
const message = `File ${filename} uploaded successfully`;

// Error handling with specific tests
try {
  processFile(file);
} catch (error) {
  if (error instanceof TypeError) {
    console.error('Invalid file type:', error);
  } else {
    console.error('Unknown error:', error);
  }
}

// Use destructuring
const { filename, size } = file;

// Meaningful variable names
const maxRetries = 3;  // ✓ Good
const mr = 3;         // ✗ Bad
```

---

## Testing Guidelines

### Python Unit Tests (pytest)

**File Structure**:
```
tests/
├── __init__.py
├── test_utils.py          # Tests for utils.py
├── test_routes.py         # Tests for routes
├── test_models.py         # Tests for models
├── fixtures.py            # Shared test data
└── conftest.py           # pytest configuration
```

**Writing Tests**:

```python
import pytest
from app import app, db
from models import Document, KeyClause

@pytest.fixture
def client():
    """Test client for API calls"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_extract_text_from_txt():
    """Test TXT file extraction"""
    from utils import extract_text_from_txt
    
    # Arrange
    test_file = 'tests/fixtures/sample.txt'
    expected = "Sample document text"
    
    # Act
    result = extract_text_from_txt(test_file)
    
    # Assert
    assert result == expected

def test_upload_requires_file(client):
    """Test that upload requires a file"""
    # Arrange & Act
    response = client.post('/upload')
    
    # Assert
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_upload_validates_file_type(client):
    """Test that only allowed file types are accepted"""
    # Arrange
    data = {'file': (BytesIO(b"content"), 'malware.exe')}
    
    # Act
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    
    # Assert
    assert response.status_code == 400
```

**Run Tests**:

```bash
# Install pytest
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=. tests/

# Run specific test file
pytest tests/test_utils.py

# Run specific test
pytest tests/test_utils.py::test_extract_text_from_txt

# Run with verbose output
pytest -v

# Stop on first failure
pytest -x
```

### JavaScript Testing (Minimal for MVP)

For now, manual testing in browser is acceptable.

```javascript
// When adding auto-testing, use Jest or Vitest
test('uploadForm validates file type', () => {
  const form = document.getElementById('uploadForm');
  const fileInput = form.querySelector('input[name="file"]');
  
  fileInput.value = 'malware.exe';
  form.dispatchEvent(new Event('submit'));
  
  // Assert error shown
  expect(document.querySelector('.error')).not.toBeNull();
});
```

---

## Git Workflow

### Commit Messages

**Format**: `<type>: <description>`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (PEP 8, formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding/updating tests
- `chore`: Build, dependencies, config

**Examples**:

```bash
git commit -m "feat: add user authentication with Flask-Login"
git commit -m "fix: route decorator missing on index() function"
git commit -m "docs: add API_DOCUMENTATION.md"
git commit -m "refactor: split app.py into blueprints"
git commit -m "perf: cache summarization results for 1 hour"
git commit -m "test: add tests for extract_text_from_pdf()"
git commit -m "chore: update requirements.txt with new dependencies"
```

**Commit Best Practices**:
- One logical change per commit
- Write in imperative mood ("Add X" not "Added X")
- Reference issues: "fix: missing route (fixes #123)"
- Keep commits atomic and reversible

### Pull Request Process

**1. Update main branch**:
```bash
git fetch upstream
git rebase upstream/main
```

**2. Push to your fork**:
```bash
git push origin feature/your-feature-name
```

**3. Create Pull Request on GitHub**:
- Title: Short description
- Description: What changed and why
- Link related issues: "Fixes #123"
- Reference code: Point to key changes

**PR Template**:
```markdown
## Description
What does this PR do?

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Changes Made
- Changed X in file Y
- Added Z to module W

## Testing
- [ ] Manual testing completed
- [ ] Unit tests added
- [ ] Test coverage: X%

## Checklist
- [ ] Code follows PEP 8
- [ ] Docstrings added
- [ ] No console.log/print left
- [ ] Tests pass locally
- [ ] Commits have clear messages

## Related Issues
Fixes #123
Related to #456
```

### Review Process

1. **CI Checks**: All tests must pass (when available)
2. **Code Review**: Minimum 1 approval from maintainer
3. **Security Review**: For auth/security changes
4. **Documentation**: Ensure documentation is updated
5. **Merge**: Squash commits into main, add to changelog

---

## Issues & Feature Requests

### Report a Bug

Use the issue template:

```markdown
**Title**: Clear, one-line description

**Description**: What happened?

**Steps to Reproduce**:
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**: What should happen?

**Actual Behavior**: What actually happened?

**Environment**:
- OS: Ubuntu 24.04
- Python: 3.11
- Flask: 3.0.0

**Additional Context**: Any other info? Error logs?

**Screenshots**: If applicable
```

### Suggest a Feature

```markdown
**Title**: Clear description of feature

**Problem Statement**: What problem does this solve?

**Proposed Solution**: How should it work?

**Alternative Solutions**: Other approaches?

**Additional Context**: Mock-ups, examples, references?
```

---

## Documentation Standards

### Code Documentation

Every function should have:
```python
def summarize_legal_document(text: str, max_sentences: int = None) -> dict:
    """Summarize a legal document using AI.
    
    Uses extractive summarization to identify the most important sentences
    from a legal document, making it easier for non-lawyers to understand.
    
    Args:
        text (str): The full document text to summarize
        max_sentences (int, optional): Maximum number of sentences in summary.
            If None, uses adaptive sizing based on document length.
            Defaults to None.
    
    Returns:
        dict: Contains 'summary' (str) and 'key_clauses' (list)
        
    Raises:
        ValueError: If text is empty or None
        Exception: If summarization fails after retries
        
    Example:
        >>> result = summarize_legal_document("This agreement...")
        >>> print(result['summary'])
        This agreement states...
        
    Note:
        For documents > 10,000 words, consider splitting before summarizing
        for better performance and accuracy.
        
    See Also:
        extract_text_from_file() - Extract text from various file formats
        identify_key_clauses_enhanced() - Extract specific clauses
    """
    pass
```

### README Updates

When adding features, update README with:
- Feature description
- New dependencies (if any)
- Usage example
- Links to docs

### API Documentation

Follow [API_DOCUMENTATION.md](API_DOCUMENTATION.md) format:
- Endpoint path and method
- Authentication required
- Request/response format
- Error codes
- Usage examples

---

## Performance Considerations

### Do's and Don'ts

```python
# ✓ Good - Query only what you need
user = User.query.filter_by(id=123).first()

# ✗ Bad - Loading unnecessary data
users = User.query.all()  # Gets all users!
user = next(u for u in users if u.id == 123)

# ✓ Good - Use database indexes
Document.query.filter_by(user_id=123).all()  # Should have index on user_id

# ✗ Bad - N+1 query problem
for doc in documents:
    author = User.query.get(doc.author_id)  # Query inside loop!

# ✓ Good - Join or eager load
docs = Document.query.join(User).filter(...)
# OR
docs = Document.query.options(joinedload(Document.author)).all()

# ✓ Good - Cache expensive operations
CLAUSE_TYPES = {
    'Termination': [...],
    'Confidentiality': [...]
}  # Computed once at startup

# ✗ Bad - Recompute every request
def get_clause_types():
    return compute_complex_regex()  # Called 1000s of times!
```

---

## Release Process (Maintainers)

1. Update version in `__init__.py`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v1.0.0`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub Release with notes
6. Deploy to production

---

## Questions & Support

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open an Issue with bug report template
- **Ideas**: Open an Issue with feature request template
- **Security Issues**: Email security@sapphire.org (don't open public issue)

---

## Code of Conduct

- Be respectful and inclusive
- Assume good intentions
- Provide constructive feedback
- Help others learn
- Report inappropriate behavior

---

## Attribution

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- GitHub contributors page
- Release notes for major contributions

---

**Welcome to the team! Happy coding! 🚀**

---

**Last Updated**: Feb 2026  
**Version**: 1.0  
**Maintained By**: Development Team
