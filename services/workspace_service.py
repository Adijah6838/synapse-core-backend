from models import db
from models.workspace import Workspace, WorkspaceMember

class WorkspaceService:
    @staticmethod
    def create_workspace(owner_id, name, description, visibility='Private'):
        # 1. Create the workspace
        new_workspace = Workspace(
            name=name,
            description=description,
            owner_id=owner_id,
            visibility=visibility
        )
        db.session.add(new_workspace)
        db.session.flush() # Flush to generate the workspace ID before committing

        # 2. Automatically add the creator as a member with the 'Manager' role
        owner_member = WorkspaceMember(
            workspace_id=new_workspace.id,
            user_id=owner_id,
            role='Manager'
        )
        db.session.add(owner_member)
        
        # 3. Commit both to the database in one transaction
        db.session.commit()
        return new_workspace, None

    @staticmethod
    def get_user_workspaces(user_id):
        # Get all workspaces where the user is a member
        memberships = WorkspaceMember.query.filter_by(user_id=user_id).all()
        workspace_ids = [m.workspace_id for m in memberships]
        
        if not workspace_ids:
            return []
            
        return Workspace.query.filter(Workspace.id.in_(workspace_ids)).all()