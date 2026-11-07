from models import db
from models.notification import Notification
from sqlalchemy.exc import IntegrityError

class NotificationService:
    @staticmethod
    def create_notification(recipient_id, title, message, event_id=None):
        try:
            notif = Notification(
                recipient_id=recipient_id,
                title=title,
                message=message,
                event_id=event_id
            )
            db.session.add(notif)
            db.session.commit()
            return notif
        except IntegrityError:
            db.session.rollback()
            return None