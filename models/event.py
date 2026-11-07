from datetime import datetime
from models import db

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=True)
    event_type = db.Column(db.String(100), nullable=False)
    aggregate_type = db.Column(db.String(50), nullable=False)
    aggregate_id = db.Column(db.Integer, nullable=False)
    
    # JSON payload to store detailed event data
    payload = db.Column(db.JSON, nullable=True) 
    
    event_version = db.Column(db.Integer, default=1, nullable=False)
    
    # Used to prevent duplicate events from being processed
    idempotency_key = db.Column(db.String(255), unique=True, nullable=True) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Event {self.event_type}>"