import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "onboarding@resend.dev")


def send_status_change_email(to_email: str, complaint_id: int, category: str, new_status: str, note: str | None):
    note_line = f"<p><strong>Note from admin:</strong> {note}</p>" if note else ""
    try:
        resend.Emails.send({
            "from": EMAIL_FROM,
            "to": to_email,
            "subject": f"Complaint #{complaint_id} status updated: {new_status}",
            "html": f"""
                <h2>Your complaint status has changed</h2>
                <p><strong>Complaint:</strong> #{complaint_id} ({category})</p>
                <p><strong>New status:</strong> {new_status}</p>
                {note_line}
            """,
        })
    except Exception as e:
        # Email failure should never break the actual status update —
        # log it, don't raise
        print(f"Failed to send status-change email to {to_email}: {e}")


def send_important_notice_email(to_email: str, title: str, body: str):
    try:
        resend.Emails.send({
            "from": EMAIL_FROM,
            "to": to_email,
            "subject": f"Important Notice: {title}",
            "html": f"""
                <h2>{title}</h2>
                <p>{body}</p>
            """,
        })
    except Exception as e:
        print(f"Failed to send notice email to {to_email}: {e}")