"""
NotificationService — creates in-app notifications and optionally
dispatches emails via SMTP.
Fully native FastAPI and legacy SQLAlchemy ORM service.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from sqlalchemy.orm import Session
from app.config import get_config
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification_schema import NotificationResponse
from app.utils.errors import NotFoundError
from app.utils.pagination import paginate_query

logger = logging.getLogger(__name__)

class NotificationService:

    # ── Create in-app notification ────────────────────────────────────────
    @staticmethod
    def notify(
        db: Session,
        user_id: str,
        title: str,
        body: str,
        *,
        type: Optional[str] = None,
        action_url: Optional[str] = None,
        interview_id: Optional[str] = None,
        send_email: bool = False,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            body=body,
            type=type,
            action_url=action_url,
            interview_id=interview_id,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        if send_email:
            try:
                user = db.query(User).get(user_id)
                if user:
                    NotificationService._send_email(user.email, title, body)
                    notif.sent_email = True
                    db.commit()
            except Exception as exc:
                logger.warning("Failed to send email notification: %s", exc)

        return notif

    # ── Mark read ─────────────────────────────────────────────────────────
    @staticmethod
    def mark_read(db: Session, notification_id: str, user_id: str) -> dict:
        from datetime import datetime, timezone
        notif = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        if not notif:
            raise NotFoundError("Notification not found.")
        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notif)
        return NotificationResponse.model_validate(notif).model_dump()

    # ── Mark all read ─────────────────────────────────────────────────────
    @staticmethod
    def mark_all_read(db: Session, user_id: str) -> int:
        from datetime import datetime, timezone
        updated_count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update(
            {"is_read": True, "read_at": datetime.now(timezone.utc)},
            synchronize_session=False
        )
        db.commit()
        return updated_count

    # ── List for user ─────────────────────────────────────────────────────
    @staticmethod
    def list_for_user(
        db: Session,
        user_id: str,
        *,
        unread_only: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        query = query.order_by(Notification.created_at.desc())

        res = paginate_query(query, page, per_page)
        # Serialize response items
        items_serialized = [NotificationResponse.model_validate(item).model_dump() for item in res["items"]]
        return {
            "items":    items_serialized,
            "total":    res["total"],
            "page":     res["page"],
            "pages":    res["pages"],
            "per_page": res["per_page"],
            "has_next": res["has_next"],
            "has_prev": res["has_prev"],
        }

    # ── Unread count ──────────────────────────────────────────────────────
    @staticmethod
    def unread_count(db: Session, user_id: str) -> int:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()

    # ── Preset notification helpers ───────────────────────────────────────
    @staticmethod
    def interview_scheduled(db: Session, interview) -> None:
        """Notify candidate + interviewer when an interview is scheduled."""
        NotificationService.notify(
            db,
            user_id=str(interview.candidate.user_id),
            title="Interview Scheduled",
            body=f"Your interview for '{interview.title}' has been scheduled.",
            type="interview_scheduled",
            action_url=f"/interviews/{interview.id}",
            interview_id=str(interview.id),
            send_email=True,
        )
        if interview.interviewer:
            NotificationService.notify(
                db,
                user_id=str(interview.interviewer.user_id),
                title="New Interview Assigned",
                body=f"You have been assigned to interview: '{interview.title}'.",
                type="interview_assigned",
                action_url=f"/interviews/{interview.id}",
                interview_id=str(interview.id),
                send_email=True,
            )

    @staticmethod
    def report_published(db: Session, interview) -> None:
        """Notify candidate when their report is published."""
        NotificationService.notify(
            db,
            user_id=str(interview.candidate.user_id),
            title="Interview Report Ready",
            body=f"Your evaluation report for '{interview.title}' is now available.",
            type="report_ready",
            action_url=f"/reports/{interview.id}",
            interview_id=str(interview.id),
            send_email=True,
        )

    # ── SMTP email dispatch ───────────────────────────────────────────────
    @staticmethod
    def _send_email(to_address: str, subject: str, body: str) -> None:
        cfg = get_config()
        server   = cfg.MAIL_SERVER
        port     = int(cfg.MAIL_PORT or 587)
        username = cfg.MAIL_USERNAME
        password = cfg.MAIL_PASSWORD
        sender   = cfg.MAIL_DEFAULT_SENDER or username

        if not all([server, username, password]):
            logger.debug("SMTP not configured — skipping email to %s", to_address)
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = sender
        msg["To"]      = to_address
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(server, port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(username, password)
            smtp.sendmail(sender, to_address, msg.as_string())

        logger.info("Email sent to %s: %s", to_address, subject)
