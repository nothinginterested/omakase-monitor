"""
Email notification module using Gmail SMTP
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from src.models import NotificationData, TimeSlot

logger = logging.getLogger(__name__)


class GmailNotifier:
    """Gmail email notifier"""

    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, app_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.app_password = app_password

    def send_notification(self, receiver_email: str, notification: NotificationData) -> bool:
        """Send email notification about new time slots"""
        try:
            subject = f"[Omakase] {notification.restaurant.name} - New Reservations Available"
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
                server.sendmail(self.sender_email, receiver_email, message.as_string())

            logger.info(f"Notification sent successfully to {receiver_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send notification: {e}", exc_info=True)
            return False

    @staticmethod
    def _build_email_body(notification: NotificationData) -> str:
        """Build HTML email body"""
        slots_html = ""
        for slot in notification.new_slots:
            price_str = f"¥{slot.price:,}" if slot.price else "N/A"
            link = slot.booking_url or notification.restaurant.detail_url
            slots_html += f"""
            <tr>
                <td>{slot.date}</td>
                <td>{slot.time}</td>
                <td>{price_str}</td>
                <td><a href="{link}">Book Now</a></td>
            </tr>
            """

        return f"""
        <html>
        <body>
            <h2>New Reservations Available: {notification.restaurant.name}</h2>
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
            <p><a href="{notification.restaurant.detail_url}">View Restaurant Page</a></p>
            <p><small>Timestamp: {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </body>
        </html>
        """
