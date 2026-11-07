from app import app
from models import db
from models.user import User
from models.workspace import Workspace, WorkspaceMember
from models.document import Document
from services.auth_service import AuthService

def seed():
    with app.app_context():
        print("Seeding database...")
        
        # 1. Create Users
        admin, _ = AuthService.register_user("admin", "admin@test.com", "password123", "Administrator")
        manager, _ = AuthService.register_user("manager", "manager@test.com", "password123", "Manager")
        editor, _ = AuthService.register_user("editor", "editor@test.com", "password123", "Editor")
        
        # 2. Create Workspace
        ws = Workspace(name="Engineering", description="Core dev team", owner_id=admin.id, visibility="Private")
        db.session.add(ws)
        db.session.flush()

        # 3. Add Members
        db.session.add(WorkspaceMember(workspace_id=ws.id, user_id=admin.id, role="Manager"))
        db.session.add(WorkspaceMember(workspace_id=ws.id, user_id=manager.id, role="Manager"))
        db.session.add(WorkspaceMember(workspace_id=ws.id, user_id=editor.id, role="Editor"))

        # 4. Create a Document
        doc = Document(
            workspace_id=ws.id,
            title="SYNAPSE Architecture",
            content="This is the initial architecture draft.",
            owner_id=editor.id,
            current_version=1,
            lock_version=1,
            status="Draft"
        )
        db.session.add(doc)
        db.session.commit()
        
        print("Database seeded successfully!")
        print("You can now log in with admin / password123")

if __name__ == '__main__':
    seed()