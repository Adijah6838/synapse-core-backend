from models import db
from models.job import BackgroundJob
from models.idempotency import IdempotencyKey
from datetime import datetime

class JobService:
    @staticmethod
    def create_job(job_type, payload=None, idempotency_key=None):
        # 1. Check if the key already exists
        if idempotency_key:
            existing_key = IdempotencyKey.query.filter_by(key=idempotency_key).first()
            if existing_key:
                return None, "Duplicate request. Job already exists."

        # 2. Create the job
        new_job = BackgroundJob(
            job_type=job_type,
            payload=payload or {},
            status='Pending'
        )
        db.session.add(new_job)
        db.session.flush() # Get the job ID

        # 3. Save the idempotency key so future requests are blocked
        if idempotency_key:
            new_key = IdempotencyKey(
                key=idempotency_key,
                response_data={"job_id": new_job.id}
            )
            db.session.add(new_key)

        db.session.commit()
        return new_job, None

    @staticmethod
    def claim_job():
        job = BackgroundJob.query.filter(
            BackgroundJob.status == 'Pending',
            BackgroundJob.available_at <= datetime.utcnow()
        ).first()

        if not job:
            return None

        job.status = 'Processing'
        job.started_at = datetime.utcnow()
        job.attempts += 1
        db.session.commit()
        
        return job