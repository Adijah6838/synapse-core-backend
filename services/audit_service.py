from models import db
from models.audit import AuditLog

class AuditService:
    @staticmethod
    def log_action(actor_id, action, entity_type, entity_id, previous_state=None, new_state=None):
        log = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            previous_state=previous_state,
            new_state=new_state
        )
        db.session.add(log)
        return log