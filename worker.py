import time
from datetime import datetime, timedelta
from app import app
from models import db
from models.job import BackgroundJob
from models.event import Event
from services.job_service import JobService
from services.audit_service import AuditService
from services.notification_service import NotificationService

def process_job(job):
    print(f"[Worker] Processing job {job.id} of type '{job.job_type}'")
    if job.job_type == 'export_document':
        time.sleep(1)
        print(f"[Worker] Successfully exported document: {job.payload.get('document_id')}")
    else:
        raise Exception("Unknown job type")

def process_events():
    """Finds unprocessed events and generates Notifications/Audit Logs."""
    events = Event.query.filter_by(processed_at=None).all()
    
    for event in events:
        print(f"[Worker] Processing event {event.id}: {event.event_type}")
        
        # 1. Create Audit Log
        actor = event.payload.get('updated_by') or event.payload.get('action_by') or 1
        AuditService.log_action(
            actor_id=actor,
            action=event.event_type,
            entity_type=event.aggregate_type,
            entity_id=event.aggregate_id,
            new_state=event.payload
        )

        # 2. Create Notification (Example: Notify user ID 1 for this demo)
        if event.event_type in ['DocumentUpdated', 'DocumentSubmitReview']:
            NotificationService.create_notification(
                recipient_id=1, # For testing, we send it to the admin
                title=f"Event: {event.event_type}",
                message=f"Document {event.aggregate_id} triggered {event.event_type}.",
                event_id=event.id
            )
            
        # 3. Mark event as processed
        event.processed_at = datetime.utcnow()
        db.session.commit()
        print(f"[Worker] Event {event.id} processed successfully.")

def run_worker():
    print("[Worker] Starting background worker...")
    
    with app.app_context():
        while True:
            # 1. Process the Event Outbox FIRST
            process_events()

            # 2. Process the Job Queue
            job = JobService.claim_job()
            
            if not job:
                time.sleep(2)
                continue

            try:
                process_job(job)
                job.status = 'Completed'
                job.completed_at = datetime.utcnow()
                db.session.commit()
                print(f"[Worker] Job {job.id} Completed.")
            except Exception as e:
                job.last_error = str(e)
                if job.attempts >= job.max_attempts:
                    job.status = 'Failed'
                else:
                    job.status = 'Pending'
                    job.available_at = datetime.utcnow() + timedelta(seconds=5 * job.attempts)
                db.session.commit()

if __name__ == '__main__':
    run_worker()