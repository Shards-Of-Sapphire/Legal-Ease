# 📡 API Documentation

Complete REST API reference for Legal-Ease endpoints, request/response formats, error codes, and usage examples.

## Base URL

**Development**: `http://localhost:5000`  
**Production**: `https://legal-ease-48vk.onrender.com`

## Authentication

**Current Status**: Not required (MVP phase)  
**Future**: Will require session-based authentication via login

All authenticated endpoints will require:
```
Cookie: session=<session_token>
```

## Response Format

### Success Response (200)

```json
{
  "success": true,
  "data": {
    "key": "value"
  },
  "message": "Optional success message"
}
```

### Error Response (4xx or 5xx)

```json
{
  "success": false,
  "error": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "details": "Additional context if available"
}
```

---

## Endpoints

### 1. GET `/`

Home page - Returns HTML upload interface.

**Method**: `GET`  
**Auth Required**: No  
**Rate Limit**: None

**Response**:
```
200 OK
Content-Type: text/html
Body: index.html content
```

**Example**:
```bash
curl http://localhost:5000/
```

---

### 2. POST `/upload`

Upload and process a legal document.

**Method**: `POST`  
**Auth Required**: No (✗ Should require auth in MVP)  
**Rate Limit**: 5 requests/minute (should be added)  
**Max File Size**: 16MB

**Request Headers**:
```
Content-Type: multipart/form-data
```

**Request Body**:
```
file: <binary file data>
  OR
captured_image: <base64 image data>
```

**Request Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes* | Document file (PDF, DOCX, TXT) |
| `captured_image` | String | Yes* | Base64-encoded image from camera |

*= One of file or captured_image required

**Success Response (200)**:
```json
{
  "success": true,
  "data": {
    "document_id": 42,
    "filename": "contract.pdf",
    "file_type": "pdf",
    "file_size": 125000,
    "summary": "This agreement establishes...",
    "key_clauses": [
      {
        "type": "Termination",
        "content": "Either party may terminate...",
        "explanation": "Specifies conditions under which the agreement can be ended"
      },
      {
        "type": "Payment Terms",
        "content": "Payment is due within 30 days...",
        "explanation": "Outlines payment obligations and schedules"
      }
    ],
    "processing_time": 12.5
  },
  "message": "Document processed successfully"
}
```

**Error Response (400)**:
```json
{
  "success": false,
  "error": "File type not supported. Please upload PDF, DOCX, or TXT files only.",
  "error_code": "INVALID_FILE_TYPE"
}
```

**Error Response (413)**:
```json
{
  "success": false,
  "error": "File too large. Please upload files smaller than 16MB.",
  "error_code": "FILE_TOO_LARGE"
}
```

**Error Response (500)**:
```json
{
  "success": false,
  "error": "Error generating summary",
  "error_code": "SUMMARIZATION_ERROR",
  "details": "Original error logged server-side"
}
```

**Curl Example**:
```bash
# Upload PDF file
curl -X POST http://localhost:5000/upload \
  -F "file=@contract.pdf"

# Upload with camera image
curl -X POST http://localhost:5000/upload \
  -F "captured_image=data:image/jpeg;base64,/9j/4AAQSkZJRg..."
```

**JavaScript Example**:
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/upload', {
  method: 'POST',
  body: formData
})
.then(res => res.json())
.then(data => {
  if (data.success) {
    console.log('Summary:', data.data.summary);
    console.log('Clauses:', data.data.key_clauses);
  }
});
```

---

### 3. GET `/document/<id>`

Retrieve a previously processed document.

**Method**: `GET`  
**Auth Required**: No (✗ Should verify user ownership in MVP)  
**Rate Limit**: None

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | Integer | Document ID |

**Success Response (200)**:
```json
{
  "success": true,
  "data": {
    "document_id": 42,
    "filename": "contract.pdf",
    "summary": "This agreement...",
    "key_clauses": [...],
    "upload_date": "2026-02-28T10:30:00Z",
    "processing_time": 12.5
  }
}
```

**Error Response (404)**:
```json
{
  "success": false,
  "error": "Document not found",
  "error_code": "NOT_FOUND"
}
```

**Curl Example**:
```bash
curl http://localhost:5000/document/42
```

**JavaScript Example**:
```javascript
fetch('/document/42')
  .then(res => res.json())
  .then(data => {
    console.log(data.data.summary);
  });
```

---

### 4. GET `/history`

Get user's document processing history (paginated).

**Method**: `GET`  
**Auth Required**: No (✗ Should require auth in MVP)  
**Rate Limit**: None

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | Integer | 1 | Page number |
| `per_page` | Integer | 10 | Items per page |

**Success Response (200)**:
```json
{
  "success": true,
  "data": {
    "documents": [
      {
        "id": 42,
        "filename": "contract.pdf",
        "file_type": "pdf",
        "file_size": 125000,
        "upload_date": "2026-02-28T10:30:00Z",
        "processing_time": 12.5,
        "summary_preview": "This agreement establishes..."
      },
      {
        "id": 41,
        "filename": "lease.docx",
        "file_type": "docx",
        "file_size": 45000,
        "upload_date": "2026-02-27T14:15:00Z",
        "processing_time": 8.2,
        "summary_preview": "This lease agreement..."
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 25,
      "total_pages": 3
    }
  }
}
```

**Error Response (500)**:
```json
{
  "success": false,
  "error": "Error loading document history",
  "error_code": "HISTORY_LOAD_ERROR"
}
```

**Curl Example**:
```bash
# Get first page
curl http://localhost:5000/history

# Get page 2 with 5 items per page
curl "http://localhost:5000/history?page=2&per_page=5"
```

**JavaScript Example**:
```javascript
fetch('/history?page=1')
  .then(res => res.json())
  .then(data => {
    data.data.documents.forEach(doc => {
      console.log(doc.filename, doc.upload_date);
    });
  });
```

---

### 5. POST `/explain`

Get a plain English explanation of a legal clause.

**Method**: `POST`  
**Auth Required**: No (✗ Should require auth in MVP)  
**Rate Limit**: 20 requests/minute (should be added)

**Request Headers**:
```
Content-Type: application/x-www-form-urlencoded
```

**Request Body**:
```
clause_text=<legal text to explain>
```

**Request Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `clause_text` | String | Yes | The legal clause (≤5000 chars) |

**Success Response (200)**:
```json
{
  "success": true,
  "data": {
    "explanation": "Indemnification Clause: This means one party agrees to protect and compensate the other party for certain types of losses, damages, or legal claims.\n\nThis clause creates binding obligations - someone must do something.\n\nPractical Impact: This has risk allocation implications - it determines who bears responsibility for potential problems.\n\nSpecific Clause Content: \"Party shall indemnify and hold harmless...\"\n\nDisclaimer: This explanation is for informational purposes only. For binding legal advice specific to your situation, consult with a qualified attorney."
  },
  "message": "Explanation generated successfully"
}
```

**Error Response (400)**:
```json
{
  "success": false,
  "error": "No clause text provided",
  "error_code": "EMPTY_CLAUSE"
}
```

**Error Response (429)**:
```json
{
  "success": false,
  "error": "Rate limit exceeded. Maximum 20 requests per minute.",
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```

**Error Response (500)**:
```json
{
  "success": false,
  "error": "Error explaining clause",
  "error_code": "EXPLANATION_ERROR"
}
```

**Curl Example**:
```bash
curl -X POST http://localhost:5000/explain \
  -d "clause_text=Party shall indemnify and hold harmless..."
```

**JavaScript Example**:
```javascript
const clauseText = "Party shall indemnify and hold harmless...";

fetch('/explain', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  },
  body: `clause_text=${encodeURIComponent(clauseText)}`
})
.then(res => res.json())
.then(data => {
  console.log(data.data.explanation);
});
```

---

### 6. GET `/terms`

Terms of Service page.

**Method**: `GET`  
**Auth Required**: No  
**Response**: HTML page (`terms.html`)

```bash
curl http://localhost:5000/terms
```

---

### 7. GET `/privacy`

Privacy Policy page.

**Method**: `GET`  
**Auth Required**: No  
**Response**: HTML page (`privacy.html`)

```bash
curl http://localhost:5000/privacy
```

---

### 8. GET `/disclaimer`

Disclaimer page.

**Method**: `GET`  
**Auth Required**: No  
**Response**: HTML page (`disclaimer.html`)

```bash
curl http://localhost:5000/disclaimer
```

---

## Error Codes

| Code | HTTP Status | Meaning | Resolution |
|------|-------------|---------|-----------|
| `INVALID_FILE_TYPE` | 400 | File format not supported | Upload PDF, DOCX, or TXT |
| `FILE_TOO_LARGE` | 413 | File exceeds 16MB limit | Compress or split file |
| `FILE_NOT_SELECTED` | 400 | No file provided | Select a file to upload |
| `TEXT_EXTRACTION_ERROR` | 400 | Could not read file | Use readable, uncorrupted file |
| `SUMMARIZATION_ERROR` | 500 | AI summary failed | No text in document |
| `EMPTY_CLAUSE` | 400 | No clause text provided | Provide text to explain |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Wait before trying again |
| `NOT_FOUND` | 404 | Document doesn't exist | Check document ID |
| `UNAUTHORIZED` | 401 | Authentication required | Login to access (future) |
| `FORBIDDEN` | 403 | Don't have permission | Cannot access others' documents (future) |
| `INTERNAL_ERROR` | 500 | Server error | Contact support |
| `DATABASE_ERROR` | 500 | Database operation failed | Try again later |

---

## Request/Response Examples

### Complete Upload Workflow

**1. User clicks upload button in form**
```
Request: POST /upload
Body: multipart/form-data with file
```

**2. Server validates and processes**
- Checks file type: ✓ .pdf
- Checks file size: ✓ 125KB < 16MB
- Extracts text: "This agreement states..."
- Generates summary via AI
- Identifies key clauses
- Saves to database

**3. Server returns results**
```json
{
  "success": true,
  "data": {
    "document_id": 42,
    "summary": "...",
    "key_clauses": [...]
  }
}
```

**4. Client displays results on same page**
```html
<div class="summary">{{ data.summary }}</div>
<div class="clauses">
  {% for clause in data.key_clauses %}
    <button onclick="explainClause('{{ clause.content }}')">
      Explain: {{ clause.type }}
    </button>
  {% endfor %}
</div>
```

---

## Code Examples

### Python (requests library)

```python
import requests

# Upload file
with open('contract.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/upload', files=files)
    
data = response.json()
print(data['data']['summary'])
```

### JavaScript (fetch)

```javascript
// Upload file
const fileInput = document.querySelector('input[type="file"]');
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data.data.summary);
```

### cURL

```bash
# Upload and pretty-print response
curl -X POST http://localhost:5000/upload \
  -F "file=@contract.pdf" \
  2>/dev/null | jq '.data | {summary, clause_count: (.key_clauses | length)}'
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `400` | Bad request (invalid input) |
| `404` | Not found |
| `413` | Request entity too large (file too big) |
| `429` | Too many requests (rate limited) |
| `500` | Internal server error |
| `503` | Service unavailable |

---

## Rate Limiting

**Current**: Not implemented (should be added Week 2)

**Planned Limits**:
- `/upload`: 5 requests/minute per IP
- `/explain`: 20 requests/minute per IP
- Others: 200 requests/hour per IP

**Response When Rate Limited**:
```json
{
  "error": "Rate limit exceeded. Maximum 5 requests per minute.",
  "retry_after": 45
}
```

**Headers**:
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1645876395
```

---

## Pagination

History endpoint supports pagination.

**Parameters**:
- `page`: Page number (1-indexed, default: 1)
- `per_page`: Items per page (default: 10, max: 100)

**Response**:
```json
{
  "data": {
    "documents": [...],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 25,
      "total_pages": 3,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

## Testing the API

### Using Postman

1. Import requests from this documentation
2. Set base URL to `http://localhost:5000`
3. Create variables for test documents
4. Run test suite

### Using Python

```python
import requests
from pathlib import Path

BASE_URL = "http://localhost:5000"

# Test upload
files = {'file': open('test.pdf', 'rb')}
r = requests.post(f"{BASE_URL}/upload", files=files)
assert r.status_code == 200
data = r.json()
doc_id = data['data']['document_id']

# Test retrieve
r = requests.get(f"{BASE_URL}/document/{doc_id}")
assert r.status_code == 200

# Test explain
r = requests.post(f"{BASE_URL}/explain", data={
    'clause_text': 'Party shall indemnify...'
})
assert r.status_code == 200

print("✓ All API tests passed")
```

---

**Last Updated**: Feb 2026  
**Version**: 1.0  
**API Stability**: Beta (Subject to change)
