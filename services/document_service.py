from models import db
from models.document import Document, DocumentVersion
from models.workspace import WorkspaceMember
from services.event_service import EventService

class DocumentService:
    @staticmethod
    def create_document(workspace_id, owner_id, title, content):
        member = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=owner_id).first()
        if not member:
            return None, "You are not a member of this workspace"

        new_doc = Document(
            workspace_id=workspace_id,
            title=title,
            content=content,
            owner_id=owner_id,
            current_version=1,
            lock_version=1,
            status='Draft'
        )
        db.session.add(new_doc)
        db.session.flush()

        initial_version = DocumentVersion(
            document_id=new_doc.id,
            version_number=1,
            content=content,
            change_summary="Initial creation",
            created_by=owner_id
        )
        db.session.add(initial_version)
        db.session.commit()
        
        return new_doc, None

    @staticmethod
    def update_document(document_id, user_id, new_content, expected_lock_version, change_summary="Updated content"):
        doc = Document.query.get(document_id)
        if not doc:
            return None, "Document not found"

        if doc.status == 'Archived':
            return None, "Cannot edit an archived document"

        # OPTIMISTIC CONCURRENCY CHECK
        if doc.lock_version != expected_lock_version:
            return None, f"Version conflict. Expected {expected_lock_version}, but server is at {doc.lock_version}. Please refresh."

        # Update the document
        doc.content = new_content
        doc.current_version += 1
        doc.lock_version += 1

        # Create the new version snapshot
        new_version = DocumentVersion(
            document_id=doc.id,
            version_number=doc.current_version,
            content=new_content,
            change_summary=change_summary,
            created_by=user_id
        )
        
        db.session.add(new_version)
        
        # Publish the event! (This is the part that was missing/not saving)
        EventService.publish_event(
            event_type="DocumentUpdated",
            aggregate_type="Document",
            aggregate_id=doc.id,
            workspace_id=doc.workspace_id,
            payload={"new_version": doc.current_version, "updated_by": user_id}
        )
        
        db.session.commit()
        
        return doc, None