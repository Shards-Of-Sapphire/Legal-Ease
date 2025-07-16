from datetime import datetime

# Models will be defined with db passed as parameter
def create_models(db):
    class Document(db.Model):
        """Model for storing document information and summaries"""
        id = db.Column(db.Integer, primary_key=True)
        filename = db.Column(db.String(255), nullable=False)
        file_type = db.Column(db.String(10), nullable=False)
        file_size = db.Column(db.Integer, nullable=False)
        original_text = db.Column(db.Text, nullable=False)
        summary = db.Column(db.Text, nullable=False)
        upload_date = db.Column(db.DateTime, default=datetime.utcnow)
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
        document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=True)
        action = db.Column(db.String(100), nullable=False)  # upload, summarize, explain
        status = db.Column(db.String(20), nullable=False)   # success, error
        error_message = db.Column(db.Text)
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        ip_address = db.Column(db.String(45))
        
        def __repr__(self):
            return f'<ProcessingLog {self.action} - {self.status}>'
    
    return Document, KeyClause, ProcessingLog