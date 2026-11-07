from models import db
from models.task import Task
from models.workspace import WorkspaceMember

class TaskService:
    @staticmethod
    def create_task(workspace_id, creator_id, title, description, priority='Medium'):
        member = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=creator_id).first()
        if not member:
            return None, "You are not a member of this workspace"

        new_task = Task(
            workspace_id=workspace_id,
            created_by=creator_id,
            title=title,
            description=description,
            priority=priority,
            status='Todo'
        )
        db.session.add(new_task)
        db.session.commit()
        return new_task, None

    @staticmethod
    def get_workspace_tasks(workspace_id):
        return Task.query.filter_by(workspace_id=workspace_id).all()