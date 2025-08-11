import os
import logging
import time
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from sqlalchemy.orm import DeclarativeBase
import utils

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///history.db")  # fallback for local/demo)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database and create tables
with app.app_context():
    # Import and create models
    from models import create_models
    Document, KeyClause, ProcessingLog = create_models(db)
    
    # Make models globally available
    globals()['Document'] = Document
    globals()['KeyClause'] = KeyClause
    globals()['ProcessingLog'] = ProcessingLog
    
    db.create_all()
    logging.info("Database tables created successfully")

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_action(action, status, ip_address, error_message=None, document_id=None):
    """Log processing activities to database"""
    try:
        log_entry = ProcessingLog(
            document_id=document_id,
            action=action,
            status=status,
            error_message=error_message,
            ip_address=ip_address
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        logging.error(f"Failed to log action: {str(e)}")

@app.route('/')
def home():
    return "LegalEase is running!"

def index():
    """Main page with file upload interface"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    start_time = time.time()
    document_id = None
    
    try:
        # Check if it's a camera capture or file upload
        captured_image = request.form.get('captured_image')
        
        if captured_image:
            # Process camera capture
            logging.info("Processing camera capture")
            
            # Extract text from image using OCR
            try:
                extracted_text = utils.extract_text_from_image(captured_image)
                if not extracted_text.strip():
                    flash('No text could be extracted from the image. Please ensure the document is clear and readable.', 'error')
                    return redirect(url_for('index'))
                
                logging.info(f"Text extracted from image, length: {len(extracted_text)}")
                
                filename = "camera_capture.jpg"
                file_type = "image"
                file_size = len(captured_image)
                
            except Exception as e:
                logging.error(f"Error extracting text from image: {str(e)}")
                log_action('extract_text', 'error', request.remote_addr, str(e))
                flash(f'Error extracting text from image: {str(e)}', 'error')
                return redirect(url_for('index'))
        else:
            # Process file upload
            if 'file' not in request.files:
                flash('No file selected', 'error')
                return redirect(url_for('index'))
            
            file = request.files['file']
            
            # Check if file was actually selected
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(url_for('index'))
            
            # Check file type
            if not allowed_file(file.filename):
                flash('File type not supported. Please upload PDF, DOCX, or TXT files only.', 'error')
                return redirect(url_for('index'))
            
            # Save file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Get file info
            file_size = os.path.getsize(filepath)
            file_type = filename.rsplit('.', 1)[1].lower()
            
            logging.info(f"File uploaded: {filename}")
            
            # Log upload
            log_action('upload', 'success', request.remote_addr)
            
            # Extract text from file
            try:
                extracted_text = utils.extract_text_from_file(filepath)
                if not extracted_text.strip():
                    flash('No text could be extracted from the file. Please check if the file contains readable text.', 'error')
                    return redirect(url_for('index'))
                
                logging.info(f"Text extracted, length: {len(extracted_text)}")
                
                # Clean up uploaded file
                os.remove(filepath)
                
            except Exception as e:
                logging.error(f"Error extracting text: {str(e)}")
                log_action('extract_text', 'error', request.remote_addr, str(e))
                flash(f'Error extracting text from file: {str(e)}', 'error')
                return redirect(url_for('index'))
        
        # Generate summary using AI
        try:
            summary_data = utils.summarize_legal_document(extracted_text)
            logging.info("Summary generated successfully")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Save to database
            document = Document(
                filename=filename,
                file_type=file_type,
                file_size=file_size,
                original_text=extracted_text,
                summary=summary_data['summary'],
                processing_time=processing_time
            )
            
            db.session.add(document)
            db.session.commit()
            document_id = document.id
            
            # Save key clauses
            for clause_data in summary_data.get('key_clauses', []):
                clause = KeyClause(
                    document_id=document_id,
                    clause_type=clause_data['type'],
                    content=clause_data['content'],
                    explanation=clause_data.get('explanation', '')
                )
                db.session.add(clause)
            
            db.session.commit()
            
            # Log successful processing
            log_action('summarize', 'success', request.remote_addr, document_id=document_id)
            
            return render_template('index.html', 
                                 filename=filename,
                                 summary=summary_data['summary'],
                                 key_clauses=summary_data.get('key_clauses', []),
                                 success=True,
                                 document_id=document_id)
            
        except Exception as e:
            logging.error(f"Error generating summary: {str(e)}")
            log_action('summarize', 'error', request.remote_addr, str(e), document_id)
            flash(f'Error generating summary: {str(e)}', 'error')
            return redirect(url_for('index'))
        
    except RequestEntityTooLarge:
        flash('File too large. Please upload files smaller than 16MB.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        log_action('upload', 'error', request.remote_addr, str(e))
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/explain', methods=['POST'])
def explain_clause():
    """Explain a specific clause in plain English"""
    try:
        clause_text = request.form.get('clause_text', '')
        if not clause_text.strip():
            return jsonify({'error': 'No clause text provided'}), 400
        
        explanation = utils.explain_legal_clause(clause_text)
        
        # Log the explanation request
        log_action('explain', 'success', request.remote_addr)
        
        return jsonify({'explanation': explanation})
        
    except Exception as e:
        logging.error(f"Error explaining clause: {str(e)}")
        log_action('explain', 'error', request.remote_addr, str(e))
        return jsonify({'error': f'Error explaining clause: {str(e)}'}), 500

@app.route('/history')
def document_history():
    """View document processing history"""
    try:
        # Get recent documents with pagination
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        documents = Document.query.order_by(Document.upload_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('history.html', documents=documents)
        
    except Exception as e:
        logging.error(f"Error fetching document history: {str(e)}")
        flash(f'Error loading document history: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/document/<int:document_id>')
def view_document(document_id):
    """View a specific document and its summary"""
    try:
        document = Document.query.get_or_404(document_id)
        key_clauses = KeyClause.query.filter_by(document_id=document_id).all()
        
        # Convert clauses to the format expected by the template
        clauses_data = []
        for clause in key_clauses:
            clauses_data.append({
                'type': clause.clause_type,
                'content': clause.content,
                'explanation': clause.explanation
            })
        
        return render_template('index.html', 
                             filename=document.filename,
                             summary=document.summary,
                             key_clauses=clauses_data,
                             success=True,
                             document_id=document.id,
                             is_historical=True)
        
    except Exception as e:
        logging.error(f"Error viewing document: {str(e)}")
        flash(f'Error loading document: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File too large. Please upload files smaller than 16MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logging.error(f"Internal server error: {str(e)}")
    flash('An internal server error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')
