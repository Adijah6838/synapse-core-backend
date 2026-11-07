from models import db
from models.document import Document
from models.user import User
from services.event_service import EventService

class WorkflowEngine:
    # Define valid transitions: (Current Status) -> (Action) -> (New Status)
    TRANSITIONS = {
        ('Draft', 'submit_review'): 'In Review',
        ('In Review', 'approve'): 'Approved',
        ('In Review', 'return_to_draft'): 'Draft',
        ('Approved', 'archive'): 'Archived'
    }

    @staticmethod
    def transition_document(document_id, user_id, action):
        doc = Document.query.get(document_id)
        if not doc:
            return None, "Document not found"

        # 1. Check if the transition is valid based on the current status
        current_status = doc.status
        transition_key = (current_status, action)
        
        if transition_key not in WorkflowEngine.TRANSITIONS:
            return None, f"Invalid transition. Cannot '{action}' a document in '{current_status}' status."

        new_status = WorkflowEngine.TRANSITIONS[transition_key]

        # 2. Role-Based Authorization Checks
        user = User.query.get(user_id)
        
        if action == 'approve' and user.role not in ['Manager', 'Administrator']:
            return None, "Unauthorized. Only Managers or Administrators can approve documents."
            
        if action == 'approve' and doc.owner_id == user.id and user.role != 'Administrator':
            return None, "Unauthorized. You cannot approve your own document."

        # 3. Apply the transition
        doc.status = new_status
        db.session.add(doc)

        # 4. Publish event for the transition
        EventService.publish_event(
            event_type=f"Document{action.title().replace('_', '')}",
            aggregate_type="Document",
            aggregate_id=doc.id,
            workspace_id=doc.workspace_id,
            payload={"new_status": new_status, "action_by": user_id}
        )

        db.session.commit()
        return doc, None