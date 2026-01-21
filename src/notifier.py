"""
Email notification module using Gmail SMTP
"""

import html
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.models import NotificationData

logger = logging.getLogger(__name__)


class GmailNotifier:
    """Gmail email notifier"""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        app_password: str
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.app_password = app_password

    def send_notification(
        self, receiver_email: str, notification: NotificationData
    ) -> bool:
        """Send email notification about new time slots"""
        try:
            restaurant_name = notification.restaurant.name
            subject = (
                f"[Omakase] {restaurant_name} - New Reservations Available"
            )
            body = self._build_email_body(notification)

            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = receiver_email

            html_part = MIMEText(body, "html")
            message.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.app_password)
                server.sendmail(
                    self.sender_email, receiver_email, message.as_string()
                )

            logger.info(f"Notification sent successfully to {receiver_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(
                f"SMTP authentication failed. Check email and app password: {e}"
            )
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error sending notification: {e}", exc_info=True
            )
            return False

    @staticmethod
    def _build_email_body(notification: NotificationData) -> str:
        """Build HTML email body with proper escaping"""
        # Escape restaurant name for HTML
        restaurant_name = html.escape(notification.restaurant.name)

        slots_html = ""
        for slot in notification.new_slots:
            # Escape all dynamic content
            date = html.escape(slot.date)
            time = html.escape(slot.time)
            price_str = f"¥{slot.price:,}" if slot.price else "N/A"
            price_escaped = html.escape(price_str)

            # URLs are validated, but still escape for safety
            link = html.escape(
                slot.booking_url or notification.restaurant.detail_url
            )

            slots_html += f"""
            <tr>
                <td>{date}</td>
                <td>{time}</td>
                <td>{price_escaped}</td>
                <td><a href="{link}">Book Now</a></td>
            </tr>
            """

        detail_url = html.escape(notification.restaurant.detail_url)
        timestamp = notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')

        return f"""
        <html>
        <body>
            <h2>New Reservations Available: {restaurant_name}</h2>
            <p>Found {len(notification.new_slots)} new time slot(s):</p>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Price</th>
                    <th>Action</th>
                </tr>
                {slots_html}
            </table>
            <p><a href="{detail_url}">View Restaurant Page</a></p>
            <p><small>Timestamp: {timestamp}</small></p>
        </body>
        </html>
        """
