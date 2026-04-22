"""Audit helpers."""

from sqlalchemy.orm import Session

from db.models import AuditLog


def write_audit(session: Session, actor_telegram_id: int, action: str, payload: str = "") -> None:
    session.add(AuditLog(actor_telegram_id=actor_telegram_id, action=action, payload=payload))
    session.flush()
