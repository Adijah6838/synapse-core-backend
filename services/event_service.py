from models import db
from models.event import Event
from datetime import datetime

class EventService:
    @staticmethod
    def publish_event(event_type, aggregate_type, aggregate_id, workspace_id=None, payload=None, idempotency_key=None):
        """
        Publishes an event to the database (Transactional Outbox pattern).
        """
        # Check for idempotency (prevent duplicate events)
        if idempotency_key:
            existing = Event.query.filter_by(idempotency_key=idempotency_key).first()
            if existing:
                return existing, None

        new_event = Event(
            workspace_id=workspace_id,
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload or {},
            idempotency_key=idempotency_key,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_event)
        # We deliberately DO NOT call db.session.commit() here.
        # The calling service (e.g., DocumentService) will commit it 
        # alongside the document update to ensure atomicity!
        
        return new_event, None