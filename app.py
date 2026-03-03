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

# Secret must be provided via environment for security
SESSION_SECRET = os.environ.get("SESSION_SECRET")
if not SESSION_SECRET or SESSION_SECRET == "dev-secret-key":
    raise RuntimeError("SESSION_SECRET environment variable must be set to a secure value")
app.secret_key = SESSION_SECRET


# Get DATABASE_URL from environment
db_url = os.environ.get("DATABASE_URL", "").strip()

# Fix Render's old postgres:// format for SQLAlchemy
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# If no DB URL is set, default to SQLite (works locally & first deploy)
if not db_url:
    db_url = "sqlite:///history.db"

# Apply DB config
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init DB
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# authentication & security extensions
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

csrf = CSRFProtect(app)

# rate limiting (prevent abuse)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configure rate limiter storage. In production set `RATELIMIT_STORAGE_URI` or `REDIS_URL`.
storage_uri = os.environ.get('RATELIMIT_STORAGE_URI') or os.environ.get('REDIS_URL') or 'memory://'
limiter = Limiter(key_func=get_remote_address, app=app, storage_uri=storage_uri)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# security / privacy config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# control storage of original document text
# if true, text is encrypted using a Fernet key, otherwise original_text is purged
from datetime import timedelta
app.config['ENCRYPT_ORIGINAL_TEXT'] = os.environ.get("ENCRYPT_ORIGINAL_TEXT", "false").lower() == "true"
app.config['ORIGINAL_TEXT_KEY'] = os.environ.get("ORIGINAL_TEXT_KEY")

# session timeout configuration
app.config['SESSION_TIMEOUT_MINUTES'] = int(os.environ.get("SESSION_TIMEOUT_MINUTES", "30"))
app.permanent_session_lifetime = timedelta(minutes=app.config['SESSION_TIMEOUT_MINUTES'])
login_manager.session_protection = "strong"

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# make current_user available in templates
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Initialize database and create tables
with app.app_context():
    # Import and create models
    from models import create_models
    User, Document, KeyClause, ProcessingLog, DocumentEvaluation, ClauseEvaluation = create_models(db)
    
    # Make models globally available
    globals()['User'] = User
    globals()['Document'] = Document
    globals()['KeyClause'] = KeyClause
    globals()['ProcessingLog'] = ProcessingLog
    globals()['DocumentEvaluation'] = DocumentEvaluation
    globals()['ClauseEvaluation'] = ClauseEvaluation
    
    db.create_all()
    logging.info("Database tables created successfully")

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_action(action, status, ip_address, error_message=None, document_id=None, file_name=None):
    """Log processing activities to database"""
    try:
        kwargs = {
            'document_id': document_id,
            'file_name': file_name,
            'action': action,
            'status': status,
            'error_message': error_message,
            'ip_address': ip_address
        }
        # attach user if available
        if current_user and hasattr(current_user, 'id'):
            kwargs['user_id'] = current_user.id
        log_entry = ProcessingLog(**kwargs)
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        logging.error(f"Failed to log action: {str(e)}")

@app.route('/')
@app.route('/index')  # ensure main UI is reachable
@login_required
def index():
    """Main page - redirect logged-in users to the dashboard"""
    return redirect(url_for('dashboard'))

# alias for health check (pre-v1)
@app.route('/health')
def home():
    return "LegalEase is running!"

@app.route('/upload', methods=['POST'])
@login_required
@limiter.limit("5 per minute")
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
                # record that the failure occurred on a camera capture
                log_action('extract_text', 'error', request.remote_addr, str(e), file_name="camera_capture.jpg")
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
            
            # Save file temporarily with unique name to avoid collisions
            filename = secure_filename(file.filename)
            unique_name = f"{int(time.time())}_{os.urandom(8).hex()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            file.save(filepath)
            
            # Get file info
            file_size = os.path.getsize(filepath)
            file_type = filename.rsplit('.', 1)[1].lower()
            
            logging.info(f"File uploaded: {filename}")
            
            # Log upload
            log_action('upload', 'success', request.remote_addr, file_name=filename)
            
            # Extract text from file
            try:
                extracted_text = utils.extract_text_from_file(filepath)
                if not extracted_text.strip():
                    flash('No text could be extracted from the file. Please check if the file contains readable text.', 'error')
                    return redirect(url_for('index'))
                
                logging.info(f"Text extracted, length: {len(extracted_text)}")
                
            except Exception as e:
                logging.error(f"Error extracting text: {str(e)}")
                log_action('extract_text', 'error', request.remote_addr, str(e), file_name=filename)
                flash(f'Error extracting text from file: {str(e)}', 'error')
                return redirect(url_for('index'))
            finally:
                # always remove temporary file if it exists
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except Exception:
                    pass
        
        # Generate summary using AI
        try:
            summary_data = utils.summarize_legal_document(extracted_text)
            logging.info("Summary generated successfully")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Save to database
            # determine how to store original text based on config
            if app.config.get('ENCRYPT_ORIGINAL_TEXT'):
                # encrypt using Fernet
                from cryptography.fernet import Fernet
                key = app.config.get('ORIGINAL_TEXT_KEY')
                if not key:
                    raise RuntimeError("ENCRYPT_ORIGINAL_TEXT is true but ORIGINAL_TEXT_KEY is not set")
                cipher = Fernet(key.encode() if isinstance(key, str) else key)
                stored_text = cipher.encrypt(extracted_text.encode()).decode()
            else:
                # purge original text to minimize risk
                stored_text = None

            document = Document(
                user_id=current_user.id,
                filename=filename,
                file_type=file_type,
                file_size=file_size,
                original_text=stored_text,
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
        log_action('upload', 'error', request.remote_addr, str(e), file_name=filename if 'filename' in locals() else None)
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/explain', methods=['POST'])
@login_required
@limiter.limit("20 per minute")
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

@app.route("/api/history")
@login_required
def api_history():
    documents = get_documents_from_db()
    documents = [
    {
        "filename": doc.filename,
        "file_type": doc.file_type,
        "file_size": doc.file_size,
        "upload_date": doc.upload_date.strftime("%Y-%m-%d %H:%M"),
        "processing_time": doc.processing_time
    }
    for doc in documents_from_db
]
    
    return jsonify({
        "success": True,
        "documents": documents
    })
        
    except Exception as e:
        logging.error(f"Error fetching document history: {str(e)}")
        flash(f'Error loading document history: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/document/<int:document_id>')
@login_required
def view_document(document_id):
    """View a specific document and its summary"""
    try:
        document = Document.query.filter_by(id=document_id, user_id=current_user.id).first_or_404()
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

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None

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

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        if not email or not password:
            flash('Email and password required', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        # re-load user from DB so it is attached and implements UserMixin properly
        user = db.session.get(User, user.id)
        from flask import session
        session.permanent = True
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            from flask import session
            session.permanent = True  # enable timeout
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials', 'error')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# User landing dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # recent documents for current user
        recent_docs = Document.query.filter_by(user_id=current_user.id).order_by(Document.upload_date.desc()).limit(10).all()
        # recent evaluations (if any)
        evaluations = []
        try:
            DocumentEvaluation = db.Model.DocumentEvaluation
            evaluations = DocumentEvaluation.query.filter_by().order_by(DocumentEvaluation.evaluation_date.desc()).limit(5).all()
        except Exception:
            evaluations = []

        return render_template('dashboard.html', recent_docs=recent_docs, evaluations=evaluations)
    except Exception as e:
        logging.error(f"Error loading dashboard: {e}")
        flash('Unable to load dashboard', 'error')
        return redirect(url_for('index'))


@app.route('/camera-tool')
@login_required
def camera_tool():
    return render_template('camera_tool.html')


@app.route('/api/analyze-camera', methods=['POST'])
@login_required
def analyze_camera():
    try:
        # Accept JSON or form-encoded
        data = request.get_json(silent=True) or request.form
        captured_image = data.get('captured_image')
        if not captured_image:
            return jsonify({'error': 'No image provided'}), 400

        # Extract text and summarize
        extracted_text = utils.extract_text_from_image(captured_image)
        summary_data = utils.summarize_legal_document(extracted_text)

        return jsonify({'summary': summary_data.get('summary', ''), 'key_clauses': summary_data.get('key_clauses', [])})
    except Exception as e:
        logging.error(f"Error analyzing camera image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')
# ===== Quality Evaluation Dashboard Routes =====
@app.route('/evaluation-dashboard')
@login_required
def evaluation_dashboard():
    """Quality evaluation dashboard for testing and metrics"""
    try:
        # Import evaluation models
        DocumentEvaluation, ClauseEvaluation = db.Model.DocumentEvaluation, db.Model.ClauseEvaluation
        
        # Get all evaluations
        evaluations = DocumentEvaluation.query.all()
        
        # Compute aggregate statistics
        from eval_utils import aggregate_evaluation_metrics, get_quality_rating
        stats = aggregate_evaluation_metrics(evaluations)
        
        return render_template('evaluation_dashboard.html', 
                             evaluations=evaluations,
                             stats=stats,
                             get_quality_rating=get_quality_rating)
    except Exception as e:
        logging.error(f"Error loading evaluation dashboard: {e}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/api/evaluate-document/<int:document_id>', methods=['POST'])
@login_required
def submit_document_evaluation(document_id):
    """API endpoint to submit document evaluation scores"""
    try:
        document = Document.query.get_or_404(document_id)
        
        # Get form data
        evaluator = request.form.get('evaluator_name', 'Anonymous')
        extraction_accuracy = int(request.form.get('extraction_accuracy', 0))
        clause_completeness = int(request.form.get('clause_completeness', 0))
        summary_accuracy = int(request.form.get('summary_accuracy', 0))
        summary_usefulness = int(request.form.get('summary_usefulness', 0))
        notes = request.form.get('notes', '')
        
        # Validate scores are 1-5
        for score in [extraction_accuracy, clause_completeness, summary_accuracy, summary_usefulness]:
            if not (1 <= score <= 5):
                return jsonify({'error': 'Scores must be 1-5'}), 400
        
        # Calculate overall score
        from eval_utils import calculate_document_score
        overall_score = calculate_document_score(
            extraction_accuracy, 
            clause_completeness, 
            summary_accuracy, 
            summary_usefulness
        )
        
        # Create evaluation record
        DocumentEvaluation = db.Model.DocumentEvaluation
        evaluation = DocumentEvaluation(
            document_id=document_id,
            evaluator_name=evaluator,
            extraction_accuracy=extraction_accuracy,
            clause_completeness=clause_completeness,
            summary_accuracy=summary_accuracy,
            summary_usefulness=summary_usefulness,
            overall_score=overall_score,
            notes=notes
        )
        
        db.session.add(evaluation)
        db.session.commit()
        
        log_action('evaluate', 'success', request.remote_addr, document_id=document_id)
        
        return jsonify({
            'success': True,
            'evaluation_id': evaluation.id,
            'overall_score': overall_score,
            'message': f'Evaluation recorded (Score: {overall_score:.2f}/5)'
        })
        
    except Exception as e:
        logging.error(f"Error submitting evaluation: {e}")
        return jsonify({'error': f'Error submitting evaluation: {str(e)}'}), 500


@app.route('/api/evaluation-stats', methods=['GET'])
@login_required
def get_evaluation_stats():
    """API endpoint to get evaluation statistics"""
    try:
        DocumentEvaluation = db.Model.DocumentEvaluation
        evaluations = DocumentEvaluation.query.all()
        
        from eval_utils import aggregate_evaluation_metrics
        stats = aggregate_evaluation_metrics(evaluations)
        
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Error fetching evaluation stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/evaluations', methods=['GET'])
@login_required
def get_evaluations():
    """Get list of all evaluations with document info"""
    try:
        DocumentEvaluation = db.Model.DocumentEvaluation
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Query evaluations with their documents
        query = DocumentEvaluation.query.order_by(DocumentEvaluation.evaluation_date.desc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        evaluations = []
        for eval_obj in paginated.items:
            evaluations.append({
                'id': eval_obj.id,
                'document_id': eval_obj.document_id,
                'document_name': eval_obj.document.filename if eval_obj.document else 'Unknown',
                'evaluator': eval_obj.evaluator_name,
                'extraction_accuracy': eval_obj.extraction_accuracy,
                'clause_completeness': eval_obj.clause_completeness,
                'summary_accuracy': eval_obj.summary_accuracy,
                'summary_usefulness': eval_obj.summary_usefulness,
                'overall_score': eval_obj.overall_score,
                'evaluation_date': eval_obj.evaluation_date.strftime('%Y-%m-%d %H:%M')
            })
        
        return jsonify({
            'evaluations': evaluations,
            'page': page,
            'per_page': per_page,
            'total': paginated.total
        })
    except Exception as e:
        logging.error(f"Error fetching evaluations: {e}")
        return jsonify({'error': str(e)}), 500
