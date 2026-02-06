
import os
import smtplib
import html
from datetime import datetime
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from typing import List

from src.logger import logger


def _parse_email_list(raw: str | None, *, fallback: List[str]) -> List[str]:
        if raw is None:
                return list(fallback)
        stripped = raw.strip()
        if not stripped:
                return list(fallback)
        items: List[str] = []
        for part in stripped.replace(";", ",").split(","):
                email_addr = part.strip()
                if email_addr:
                        items.append(email_addr)
        return items or list(fallback)


def _email_theme(email_type: str) -> dict:
    normalized = (email_type or "default").strip().lower()
    if normalized in {"none", "no_tenders", "no-results", "no_results", "empty"}:
        return {
            "accent": "#6B7280",  # gray
            "title": "No Tenders Found",
            "badge": "No Results",
        }
    if normalized in {"special_monday", "monday", "weekly", "special_wednesday", "wednesday", "special_friday", "friday"}:
            return {
                    "accent": "#6D28D9",  # violet
                    "title": "Scheduled Batch Report",
                    "badge": "Scheduled Batch",
            }
    if normalized in {"pdf", "pdf_report", "analysis"}:
            return {
                    "accent": "#0F766E",  # teal
                    "title": "Tender Analysis Report",
                    "badge": "PDF Analysis",
            }
    return {
            "accent": "#2563EB",  # blue
            "title": "Tender Report",
            "badge": "Automated",
    }


def _build_email_bodies(
        *,
        report_title: str,
        total_tenders: int,
        filename: str,
        email_type: str,
) -> tuple[str, str]:
        safe_title = html.escape(report_title or "Tender Report")
        safe_filename = html.escape(filename or "report.xlsx")
        theme = _email_theme(email_type)
        now_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        text_body = (
                f"{theme['title']}\n"
                f"{report_title}\n\n"
                f"Total tenders processed: {total_tenders}\n"
                f"Attachment: {filename}\n"
                f"Generated at: {now_local}\n"
        )

        # Inline-styled HTML (works better across email clients than external CSS)
        accent = theme["accent"]
        badge = html.escape(theme["badge"])
        header_title = html.escape(theme["title"])

        html_body = f"""
<!doctype html>
<html lang=\"en\">
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <meta name=\"x-apple-disable-message-reformatting\" />
        <title>{header_title}</title>
    </head>
    <body style=\"margin:0;padding:0;background:#F3F4F6;\">
        <div style=\"display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;\">
            {safe_title} — {total_tenders} tenders — attachment: {safe_filename}
        </div>

        <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"background:#F3F4F6;\">
            <tr>
                <td align=\"center\" style=\"padding:24px 12px;\">
                    <table role=\"presentation\" width=\"600\" cellspacing=\"0\" cellpadding=\"0\" style=\"width:600px;max-width:100%;background:#FFFFFF;border-radius:14px;overflow:hidden;border:1px solid #E5E7EB;\">
                        <tr>
                            <td style=\"padding:18px 20px;background:{accent};\">
                                <div style=\"font-family:Segoe UI, Arial, sans-serif;color:#FFFFFF;font-size:18px;font-weight:700;line-height:1.25;\">{header_title}</div>
                                <div style=\"margin-top:6px;font-family:Segoe UI, Arial, sans-serif;color:#EAF2FF;font-size:13px;line-height:1.35;\">{safe_title}</div>
                            </td>
                        </tr>

                        <tr>
                            <td style=\"padding:18px 20px;\">
                                <div style=\"font-family:Segoe UI, Arial, sans-serif;color:#111827;font-size:14px;line-height:1.6;\">
                                    <div style=\"margin-bottom:10px;\">Dear Team,</div>
                                    <div style=\"margin-bottom:14px;\">Please find attached the report.</div>

                                    <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"border-collapse:separate;border-spacing:0;\">
                                        <tr>
                                            <td style=\"padding:12px 14px;border:1px solid #E5E7EB;border-radius:12px;background:#FAFAFA;\">
                                                <div style=\"display:inline-block;padding:4px 10px;border-radius:999px;background:rgba(255,255,255,0.2);border:1px solid #E5E7EB;color:#374151;font-family:Segoe UI, Arial, sans-serif;font-size:12px;font-weight:600;\">{badge}</div>
                                                <div style=\"margin-top:10px;font-family:Segoe UI, Arial, sans-serif;color:#111827;font-size:13px;\"><strong>Total tenders:</strong> {total_tenders}</div>
                                                <div style=\"margin-top:6px;font-family:Segoe UI, Arial, sans-serif;color:#111827;font-size:13px;\"><strong>Attachment:</strong> {safe_filename}</div>
                                                <div style=\"margin-top:6px;font-family:Segoe UI, Arial, sans-serif;color:#6B7280;font-size:12px;\">Generated at {now_local}</div>
                                            </td>
                                        </tr>
                                    </table>

                                    <div style=\"margin-top:16px;color:#374151;font-family:Segoe UI, Arial, sans-serif;font-size:12.5px;\">
                                        This is an automated email generated by the Tender Service.
                                    </div>
                                </div>
                            </td>
                        </tr>

                        <tr>
                            <td style=\"padding:14px 20px;background:#F9FAFB;border-top:1px solid #E5E7EB;\">
                                <div style=\"font-family:Segoe UI, Arial, sans-serif;color:#6B7280;font-size:12px;line-height:1.5;\">
                                    Best regards,<br />
                                    Tender Service
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
</html>
""".strip()

        return text_body, html_body


def _build_notification_bodies(
        *,
        report_title: str,
        message: str,
        email_type: str,
) -> tuple[str, str]:
        safe_title = html.escape(report_title or "Notification")
        safe_message = html.escape(message or "")
        theme = _email_theme(email_type)
        now_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        text_body = (
                f"{theme['title']}\n"
                f"{report_title}\n\n"
                f"{message}\n\n"
                f"Generated at: {now_local}\n"
        )

        accent = theme["accent"]
        badge = html.escape(theme["badge"])
        header_title = html.escape(theme["title"])

        html_body = f"""
<!doctype html>
<html lang=\"en\">
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <meta name=\"x-apple-disable-message-reformatting\" />
        <title>{header_title}</title>
    </head>
    <body style=\"margin:0;padding:0;background:#F3F4F6;\">
        <div style=\"display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;\">
            {safe_title}
        </div>

        <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"background:#F3F4F6;\">
            <tr>
                <td align=\"center\" style=\"padding:24px 12px;\">
                    <table role=\"presentation\" width=\"600\" cellspacing=\"0\" cellpadding=\"0\" style=\"width:600px;max-width:100%;background:#FFFFFF;border-radius:14px;overflow:hidden;border:1px solid #E5E7EB;\">
                        <tr>
                            <td style=\"padding:18px 20px;background:{accent};\">
                                <div style=\"font-family:Segoe UI, Arial, sans-serif;color:#FFFFFF;font-size:18px;font-weight:700;line-height:1.25;\">{header_title}</div>
                                <div style=\"margin-top:6px;font-family:Segoe UI, Arial, sans-serif;color:#F3F4F6;font-size:13px;line-height:1.35;\">{safe_title}</div>
                            </td>
                        </tr>

                        <tr>
                            <td style=\"padding:18px 20px;\">
                                <div style=\"font-family:Segoe UI, Arial, sans-serif;color:#111827;font-size:14px;line-height:1.6;\">
                                    <div style=\"margin-bottom:10px;\">Dear Team,</div>
                                    <div style=\"margin-bottom:14px;\">{safe_message}</div>

                                    <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"border-collapse:separate;border-spacing:0;\">
                                        <tr>
                                            <td style=\"padding:12px 14px;border:1px solid #E5E7EB;border-radius:12px;background:#FAFAFA;\">
                                                <div style=\"display:inline-block;padding:4px 10px;border-radius:999px;background:#FFFFFF;border:1px solid #E5E7EB;color:#374151;font-family:Segoe UI, Arial, sans-serif;font-size:12px;font-weight:600;\">{badge}</div>
                                                <div style=\"margin-top:10px;font-family:Segoe UI, Arial, sans-serif;color:#6B7280;font-size:12px;\">Generated at {now_local}</div>
                                            </td>
                                        </tr>
                                    </table>

                                    <div style=\"margin-top:16px;color:#374151;font-family:Segoe UI, Arial, sans-serif;font-size:12.5px;\">
                                        This is an automated notification generated by the Tender Service.
                                    </div>
                                </div>
                            </td>
                        </tr>

                        <tr>
                            <td style=\"padding:14px 20px;background:#F9FAFB;border-top:1px solid #E5E7EB;\">
                                <div style=\"font-family:Segoe UI, Arial, sans-serif;color:#6B7280;font-size:12px;line-height:1.5;\">
                                    Best regards,<br />
                                    Tender Service
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
</html>
""".strip()

        return text_body, html_body

def get_email_config() -> tuple[str, List[str], List[str], str]:
    """Get email configuration from environment variables."""
    sender_email = os.getenv("SENDER_EMAIL", "itgel6708@gmail.com")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    # Allow overriding recipients via env vars, but keep current defaults.
    receiver_emails = _parse_email_list(
        os.getenv("RECEIVER_EMAILS") or os.getenv("RECEIVER_EMAIL"),
        fallback=["itgel.o@techpack.mn"],
    )
    # cc_emails = _parse_email_list(os.getenv("CC_EMAILS") or os.getenv("CC_EMAIL"), fallback=[])
    receiver_emails = ["itgel.o@techpack.mn", "suvderdene.g@mcst.mn", "temuulen.b@mcst.mn"]
    cc_emails = ["nomin.ts@mcst.mn", "Udval.B@mcs.mn", "erdenebileg.b@techpack.mn"]

    if not app_password:
        logger.error("GMAIL_APP_PASSWORD not configured")
        raise ValueError("GMAIL_APP_PASSWORD environment variable not set")

    return sender_email, receiver_emails, cc_emails, app_password

def get_speciel_email_config() -> tuple[str, List[str], List[str], str]:
    """Get special email configuration from environment variables."""
    sender_email = os.getenv("SENDER_EMAIL", "itgel6708@gmail.com")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    # Allow overriding recipients via env vars, but keep current defaults.
    # receiver_emails = _parse_email_list(
    #     os.getenv("RECEIVER_EMAILS") or os.getenv("RECEIVER_EMAIL"),
    #     fallback=["itgel.o@techpack.mn"],
    # )
    # cc_emails = _parse_email_list(os.getenv("CC_EMAILS") or os.getenv("CC_EMAIL"), fallback=[])
    receiver_emails = ["itgel.o@techpack.mn", "suvderdene.g@mcst.mn", "temuulen.b@mcst.mn"]
    cc_emails = ["nomin.ts@mcst.mn", "Udval.B@mcs.mn", "erdenebileg.b@techpack.mn"]

    if not app_password:
        logger.error("GMAIL_APP_PASSWORD not configured")
        raise ValueError("GMAIL_APP_PASSWORD environment variable not set")

    return sender_email, receiver_emails, cc_emails, app_password

def send_notification_email(
        report_title: str,
        message: str,
        type: str = "default",
        mail_type: str = "default",
    ) -> None:
        """Send a notification email without attachments (e.g., no tenders found)."""
        #check type is default or special
        sender_email, receiver_emails, cc_emails, app_password = get_email_config() if mail_type == "default" else get_speciel_email_config()


        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = ", ".join(receiver_emails)
        if cc_emails:
            msg["Cc"] = ", ".join(cc_emails)

        theme = _email_theme(type)
        msg["Subject"] = f"{theme['title']} - {report_title} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        text_body, html_body = _build_notification_bodies(
            report_title=report_title,
            message=message,
            email_type=type,
        )
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)
            logger.info(f"Notification email sent successfully to {receiver_emails} with CC to {cc_emails}")
        except Exception as e:
            logger.error(f"Failed to send notification email: {e}", exc_info=True)
            raise

def send_email(
    filename: str, 
    filedata: bytes, 
    report_title: str,
    total_tenders: int = 0,
    type: str = "default",
    mail_type: str = "default"
):
    """Send an email with the given attachment and report details."""
    sender_email, receiver_emails, cc_emails, app_password = get_email_config() if mail_type == "default" else get_speciel_email_config()

    # Root container must be 'mixed' when there are attachments.
    msg = MIMEMultipart("mixed")
    msg["From"] = sender_email
    msg["To"] = ", ".join(receiver_emails)
    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)

    theme = _email_theme(type)
    msg["Subject"] = f"{theme['title']} - {report_title} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Alternative (plain + html) body.
    text_body, html_body = _build_email_bodies(
        report_title=report_title,
        total_tenders=total_tenders,
        filename=filename,
        email_type=type,
    )
    alternative = MIMEMultipart("alternative")
    alternative.attach(MIMEText(text_body, "plain", "utf-8"))
    alternative.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alternative)

    # Attach the file
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(filedata)
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename="{filename}"',
    )
    msg.attach(part)

    try:
        # Send the email via Gmail SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
        logger.info(f"Email sent successfully to {receiver_emails} with CC to {cc_emails}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
        raise
    