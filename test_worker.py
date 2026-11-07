from app import app
from models import db, Event, AuditLog, Notification
from datetime import datetime

with app.app_context():
    events = Event.query.filter_by(processed_at=None).all()
    print(f"Found {len(events)} unprocessed events.")

    for event in events:
        try:
            print(f"Trying event {event.id} ({event.event_type})...")
            
            # 1. Try Audit Log
            from services.audit_service import AuditService
            AuditService.log_action(1, event.event_type, event.aggregate_type, event.aggregate_id, new_state=event.payload)
            db.session.flush() # Force it to hit the database immediately to catch errors
            print("  -> Audit log added to session.")
            
            # 2. Try Notification
            from services.notification_service import NotificationService
            notif = NotificationService.create_notification(1, "Test", "Msg", event.id)
            print(f"  -> Notification created: {notif is not None}")
            
            # 3. Mark Processed
            event.processed_at = datetime.utcnow()
            db.session.commit()
            print("  -> Success!")
            
        except Exception as e:
            import traceback
            print("\n--- ERROR OCCURRED ---")
            traceback.print_exc()
            db.session.rollback()
            print("----------------------\n")

    print("Final counts:")
    print("Audit Logs:", AuditLog.query.count())
    print("Notifications:", Notification.query.count())