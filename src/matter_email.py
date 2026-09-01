"""Business decisions for a legal-tech matter intake workflow."""

from datetime import date
from typing import Any, Callable


EmailSender = Callable[[dict[str, str], str], dict[str, Any]]
PERMITTED_RECIPIENT = "chenhua@changba.com"


def planned_email(matter: dict[str, Any], today: date) -> tuple[str, str] | None:
    """Return the next message kind and subject, or None when no message is due."""
    if matter["payment_received"]:
        if matter["signed_document_delivered"]:
            return "receipt", f"Receipt for matter {matter['matter_id']}"
        return "signed-document", f"Signed document ready for matter {matter['matter_id']}"
    deadline = date.fromisoformat(matter["deadline"])
    if deadline >= today and (deadline - today).days <= 3:
        return "deadline", f"Deadline follow-up for matter {matter['matter_id']}"
    return None


def send_matter_email(matter: dict[str, Any], today: date, sender: EmailSender) -> dict[str, Any] | None:
    plan = planned_email(matter, today)
    if plan is None:
        return None
    kind, subject = plan
    body = (
        f"<p>Matter {matter['matter_id']}: {kind.replace('-', ' ')}.</p>"
        f"<p>Next deadline: {matter['deadline']}.</p>"
    )
    return sender(
        {"to": PERMITTED_RECIPIENT, "subject": subject, "html": body},
        f"matter-{matter['matter_id']}-{kind}",
    )
