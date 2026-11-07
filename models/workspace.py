from datetime import datetime
from models import db

class Workspace(db.Model):
    __tablename__ = 'workspaces'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    visibility = db.Column(db.String(20), default='Private', nullable=False) # Private or Public
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # This creates a relationship so we can easily get all members of a workspace
    members = db.relationship('WorkspaceMember', backref='workspace', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Workspace {self.name}>"


class WorkspaceMember(db.Model):
    __tablename__ = 'workspace_members'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), default='Editor', nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # This prevents a user from being added to the same workspace twice
    __table_args__ = (db.UniqueConstraint('workspace_id', 'user_id', name='_workspace_user_uc'),)

    def __repr__(self):
        return f"<WorkspaceMember workspace_id={self.workspace_id} user_id={self.user_id}>"