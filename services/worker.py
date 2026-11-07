import time
from datetime import datetime, timedelta
from app import app
from models import db
from models.job import BackgroundJob
from services.job_service import JobService

def process_job(job):
    """Simulates processing a job based on its type."""
    print(f"[Worker] Processing job {job.id} of type '{job.job_type}'")
    
    if job.job_type == 'export_document':
        # Simulate a time-consuming task
        time.sleep(2)
        print(f"[Worker] Successfully exported document: {job.payload.get('document_id')}")
    else:
        print(f"[Worker] Unknown job type: {job.job_type}")
        raise Exception("Unknown job type")

def run_worker():
    """The main worker loop."""
    print("[Worker] Starting background worker...")
    
    with app.app_context():
        while True:
            job = JobService.claim_job()
            
            if not job:
                # If no jobs, sleep for 2 seconds and check again
                time.sleep(2)
                continue

            try:
                # Execute the job
                process_job(job)
                
                # Mark as Completed
                job.status = 'Completed'
                job.completed_at = datetime.utcnow()
                db.session.commit()
                print(f"[Worker] Job {job.id} Completed.")
                
            except Exception as e:
                # Handle failures and retries
                job.last_error = str(e)
                if job.attempts >= job.max_attempts:
                    job.status = 'Failed'
                    print(f"[Worker] Job {job.id} FAILED permanently.")
                else:
                    job.status = 'Pending' # Put it back in queue
                    # Exponential backoff (e.g., wait 5 seconds per attempt)
                    job.available_at = datetime.utcnow() + timedelta(seconds=5 * job.attempts)
                    print(f"[Worker] Job {job.id} failed. Retrying in {5 * job.attempts} seconds.")
                
                db.session.commit()

if __name__ == '__main__':
    run_worker()