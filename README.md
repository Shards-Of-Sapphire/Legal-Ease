# LegalEase - Legal Document Summarizer

## Overview

LegalEase is a web-based legal document summarizer that allows users to upload legal documents (PDF, DOCX, or TXT) and receive AI-powered summaries in plain English. The application uses Flask as the backend framework and OpenAI's API for document processing and summarization.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Vanilla HTML5, CSS3, and JavaScript
- **UI Framework**: Bootstrap 5 with dark theme
- **Icons**: Font Awesome 6.0
- **Branding**: Dual branding with LegalEase project logo and Sapphire developer team branding
- **Features**: 
  - Drag-and-drop file upload interface
  - Real-time camera capture for document scanning
  - Real-time file validation
  - Progress tracking with visual feedback
  - Document history viewing with pagination
  - Responsive design for mobile and desktop

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Structure**: Simple monolithic architecture with separation of concerns
- **File Processing**: Modular text extraction system supporting multiple file formats
- **Data Persistence**: All documents, summaries, and processing logs stored in database
- **Session Management**: Flask sessions with configurable secret key

## Key Components

### File Processing System
- **Supported Formats**: PDF (PyMuPDF), DOCX (python-docx), TXT, Camera Images (OCR)
- **Upload Constraints**: 16MB file size limit
- **Security**: Filename sanitization and extension validation
- **Text Extraction**: Format-specific extraction methods in `utils.py`
- **Camera Scanner**: Real-time camera capture with OCR text extraction using Tesseract

### Web Interface
- **Upload Interface**: Modern drag-and-drop file upload with visual feedback
- **Flash Messaging**: User feedback system for errors and success messages
- **Progress Tracking**: Real-time upload and processing progress indicators

### AI Processing
- **Provider**: Enhanced SUMY Library with NLTK (Local processing, no API required)
- **Algorithm**: Intelligent Latent Semantic Analysis (LSA) with sentence importance scoring
- **Document Type Detection**: Automatic identification of legal document types (NDA, Employment, Service, etc.)
- **Enhanced Summarization**: Context-aware summaries with readability improvements
- **Advanced Clause Detection**: Pattern-based identification with structured explanations
- **Intelligent Explanations**: Multi-layered clause analysis including structure, implications, and practical impact
- **Error Handling**: Graceful degradation with intelligent fallback systems

## Data Flow

1. **Input Method**: User uploads document or captures photo through web interface
2. **Validation**: File type and size validation on both client and server
3. **Storage**: Temporary file storage in uploads directory (file upload only)
4. **Text Extraction**: Format-specific text extraction using appropriate libraries or OCR for images
5. **AI Processing**: Local text summarization using enhanced SUMY library
6. **Database Storage**: Document metadata, extracted text, summary, and key clauses saved to PostgreSQL
7. **Response**: Summarized content returned to user interface with database confirmation

## External Dependencies

### Python Libraries
- **Flask**: Web framework and routing
- **Flask-SQLAlchemy**: Database ORM integration
- **PostgreSQL**: Primary database with psycopg2-binary driver
- **PyMuPDF (fitz)**: PDF text extraction
- **python-docx**: DOCX document processing
- **SUMY**: Text summarization library
- **NLTK**: Natural language processing toolkit
- **NumPy**: Mathematical operations for text processing
- **Werkzeug**: File handling utilities
- **Pillow**: Image processing for OCR
- **pytesseract**: OCR text extraction from images

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome**: Icon library
- **CDN-based**: External dependencies loaded from CDNs

### Environment Variables
- `SESSION_SECRET`: Flask session security (defaults to dev key)
- No external API keys required - all processing is done locally

## Deployment Strategy

### Development
- **Entry Point**: `main.py` runs Flask development server
- **Debug Mode**: Enabled for development with hot reload
- **Host Configuration**: Binds to all interfaces (0.0.0.0:5000)

### Production Considerations
- **File Storage**: Local filesystem (uploads directory)
- **Scalability**: Single-instance deployment suitable for small to medium usage
- **Security**: Environment-based configuration for sensitive data
- **Error Handling**: Comprehensive error handling for file processing and API calls

### File Structure
```
/
├── app.py              # Main Flask application
├── main.py             # Application entry point
├── utils.py            # Text extraction utilities
├── templates/
│   └── index.html      # Main upload interface
├── static/
│   ├── css/style.css   # Custom styles
│   └── js/script.js    # Frontend JavaScript
└── uploads/            # Temporary file storage
```

The application follows a simple MVC pattern with clear separation between presentation (templates), business logic (app.py), and utilities (utils.py). The architecture prioritizes simplicity and ease of maintenance while providing a robust file processing pipeline.