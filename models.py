from datetime import datetime, timezone
from flask_login import UserMixin

# Models will be defined with db passed as parameter
# create_models is idempotent; repeated calls return the same classes

def create_models(db):
    # if models already registered, return them
    if hasattr(db.Model, '_initialized_models') and db.Model._initialized_models:
        return (
            db.Model.User,
            db.Model.Document,
            db.Model.KeyClause,
            db.Model.ProcessingLog,
            db.Model.DocumentEvaluation,
            db.Model.ClauseEvaluation,
        )

    class User(db.Model, UserMixin):
        """Simple user model for authentication"""
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        
        # Relationships
        documents = db.relationship('Document', backref='owner', lazy=True)
        logs = db.relationship('ProcessingLog', backref='user', lazy=True)

        def __repr__(self):
            return f'<User {self.email}>'

    class Document(db.Model):
        """Model for storing document information and summaries"""
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
        filename = db.Column(db.String(255), nullable=False)
        file_type = db.Column(db.String(10), nullable=False)
        file_size = db.Column(db.Integer, nullable=False)
        # original_text may be encrypted or omitted for privacy
        original_text = db.Column(db.Text, nullable=True)
        summary = db.Column(db.Text, nullable=False)
        upload_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        processing_time = db.Column(db.Float)  # Time taken to process in seconds
        
        # Relationship to key clauses
        key_clauses = db.relationship('KeyClause', backref='document', lazy=True, cascade='all, delete-orphan')
        
        def __repr__(self):
            return f'<Document {self.filename}>'

    class KeyClause(db.Model):
        """Model for storing identified key clauses"""
        id = db.Column(db.Integer, primary_key=True)
        document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
        clause_type = db.Column(db.String(100), nullable=False)
        content = db.Column(db.Text, nullable=False)
        explanation = db.Column(db.Text)
        
        def __repr__(self):
            return f'<KeyClause {self.clause_type}>'

    class ProcessingLog(db.Model):
        """Model for logging processing activities"""
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
        document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=True)
        file_name = db.Column(db.String(255))
        action = db.Column(db.String(100), nullable=False)  # upload, summarize, explain
        status = db.Column(db.String(20), nullable=False)   # success, error
        error_message = db.Column(db.Text)
        timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        ip_address = db.Column(db.String(45))
        
        def __repr__(self):
            return f'<ProcessingLog {self.action} - {self.status}>'

    class DocumentEvaluation(db.Model):
        """Model for storing document quality evaluations"""
        id = db.Column(db.Integer, primary_key=True)
        document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
        evaluator_name = db.Column(db.String(255))  # Name of evaluator (lawyer, QA, etc)
        
        # Scoring dimensions (1-5 scale)
        extraction_accuracy = db.Column(db.Integer)  # How accurate was text extraction
        clause_completeness = db.Column(db.Integer)  # % of important clauses found
        summary_accuracy = db.Column(db.Integer)  # No false information
        summary_usefulness = db.Column(db.Integer)  # How helpful for user
        
        # Overall score and notes
        overall_score = db.Column(db.Float)  # Average of the above
        notes = db.Column(db.Text)  # Evaluator comments
        evaluation_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        
        def __repr__(self):
            return f'<DocumentEvaluation doc_id={self.document_id} score={self.overall_score}>'

    class ClauseEvaluation(db.Model):
        """Model for storing per-clause evaluation results"""
        id = db.Column(db.Integer, primary_key=True)
        document_evaluation_id = db.Column(db.Integer, db.ForeignKey('document_evaluation.id'), nullable=False)
        key_clause_id = db.Column(db.Integer, db.ForeignKey('key_clause.id'), nullable=False)
        
        # Was this clause correctly identified?
        is_correct = db.Column(db.Boolean, default=True)
        # Should this clause have been identified but wasn't?
        is_false_negative = db.Column(db.Boolean, default=False)
        # Notes about this clause
        notes = db.Column(db.Text)
        
        def __repr__(self):
            return f'<ClauseEvaluation evaluation_id={self.document_evaluation_id}>'

    # cache classes on the base so subsequent calls return them
    db.Model._initialized_models = True
    db.Model.User = User
    db.Model.Document = Document
    db.Model.KeyClause = KeyClause
    db.Model.ProcessingLog = ProcessingLog
    db.Model.DocumentEvaluation = DocumentEvaluation
    db.Model.ClauseEvaluation = ClauseEvaluation
    
    return User, Document, KeyClause, ProcessingLog, DocumentEvaluation, ClauseEvaluation
