from datetime import datetime
from models import db

class BackgroundJob(db.Model):
    __tablename__ = 'background_jobs'

    id = db.Column(db.Integer, primary_key=True)
    job_type = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(50), default='Pending', nullable=False) # Pending, Processing, Completed, Failed, Retry Scheduled
    
    attempts = db.Column(db.Integer, default=0, nullable=False)
    max_attempts = db.Column(db.Integer, default=3, nullable=False)
    available_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    last_error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BackgroundJob {self.job_type} ({self.status})>"