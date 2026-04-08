"""
NotificationService — creates in-app notifications and optionally
dispatches emails via SMTP (no external service required).
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from flask import current_app

from app import db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification_schema import NotificationSchema
from app.utils.errors import NotFoundError
from app.utils.pagination import paginate_query

logger = logging.getLogger(__name__)
_schema = NotificationSchema()


class NotificationService:

    # ── Create in-app notification ────────────────────────────────────────
    @staticmethod
    def notify(
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
        db.session.add(notif)
        db.session.commit()

        if send_email:
            try:
                user = User.query.get(user_id)
                if user:
                    NotificationService._send_email(user.email, title, body)
                    notif.sent_email = True
                    db.session.commit()
            except Exception as exc:
                # Email failure must never break the main flow
                logger.warning("Failed to send email notification: %s", exc)

        return notif

    # ── Mark read ─────────────────────────────────────────────────────────
    @staticmethod
    def mark_read(notification_id: str, user_id: str) -> dict:
        from datetime import datetime, timezone
        notif = Notification.query.filter_by(
            id=notification_id, user_id=user_id
        ).first()
        if not notif:
            raise NotFoundError("Notification not found.")
        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
        db.session.commit()
        return _schema.dump(notif)

    # ── Mark all read ─────────────────────────────────────────────────────
    @staticmethod
    def mark_all_read(user_id: str) -> int:
        from datetime import datetime, timezone
        updated = (
            Notification.query
            .filter_by(user_id=user_id, is_read=False)
            .update({"is_read": True, "read_at": datetime.now(timezone.utc)})
        )
        db.session.commit()
        return updated

    # ── List for user ─────────────────────────────────────────────────────
    @staticmethod
    def list_for_user(
        user_id: str,
        *,
        unread_only: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        q = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            q = q.filter_by(is_read=False)
        q = q.order_by(Notification.created_at.desc())
        return paginate_query(q, page, per_page, _schema)

    # ── Unread count ──────────────────────────────────────────────────────
    @staticmethod
    def unread_count(user_id: str) -> int:
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    # ── Preset notification helpers ───────────────────────────────────────
    @staticmethod
    def interview_scheduled(interview) -> None:
        """Notify candidate + interviewer when an interview is scheduled."""
        NotificationService.notify(
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
                user_id=str(interview.interviewer.user_id),
                title="New Interview Assigned",
                body=f"You have been assigned to interview: '{interview.title}'.",
                type="interview_assigned",
                action_url=f"/interviews/{interview.id}",
                interview_id=str(interview.id),
                send_email=True,
            )

    @staticmethod
    def report_published(interview) -> None:
        """Notify candidate when their report is published."""
        NotificationService.notify(
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
        cfg = current_app.config
        server   = cfg.get("MAIL_SERVER")
        port     = int(cfg.get("MAIL_PORT", 587))
        username = cfg.get("MAIL_USERNAME")
        password = cfg.get("MAIL_PASSWORD")
        sender   = cfg.get("MAIL_DEFAULT_SENDER", username)

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
