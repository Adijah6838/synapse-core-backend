from models.document import Document
from models.task import Task
from models.job import BackgroundJob
from models.user import User

class AnalyticsService:
    @staticmethod
    def get_overview():
        return {
            "total_users": User.query.count(),
            "total_documents": Document.query.count(),
            "active_tasks": Task.query.filter(Task.status != 'Completed').count(),
            "completed_tasks": Task.query.filter_by(status='Completed').count(),
            "pending_jobs": BackgroundJob.query.filter_by(status='Pending').count(),
            "failed_jobs": BackgroundJob.query.filter_by(status='Failed').count()
        }