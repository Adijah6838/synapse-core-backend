from datetime import datetime
from models import db

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Versioning and Concurrency
    current_version = db.Column(db.Integer, default=1, nullable=False)
    lock_version = db.Column(db.Integer, default=1, nullable=False) 
    
    status = db.Column(db.String(50), default='Draft', nullable=False) # Draft, In Review, Approved, Archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to versions
    versions = db.relationship('DocumentVersion', backref='document', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document {self.title} (v{self.current_version})>"


class DocumentVersion(db.Model):
    __tablename__ = 'document_versions'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=True)
    change_summary = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DocumentVersion doc_id={self.document_id} v{self.version_number}>"