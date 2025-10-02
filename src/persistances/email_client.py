"""Email client for sending activation codes."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Protocol

logger: logging.Logger = logging.getLogger(name=__name__)


class EmailClientInterface(Protocol):
    """Interface for email sending."""

    def send_activation_email(self, to_email: str, activation_code: str) -> bool:
        """Send activation email with code.

        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        ...  # No implementation, just the signature!


class MockMailer:
    """Mock email client for testing/development."""

    def send_activation_email(self, to_email: str, activation_code: str) -> bool:
        """Mock implementation - just logs the activation code."""
        logger.info("ACTIVATION EMAIL - To: %s", to_email)
        logger.info("ACTIVATION CODE: %s", activation_code)
        print(f"\n{'='*50}")
        print("📧 ACTIVATION EMAIL")
        print(f"📮 To: {to_email}")
        print(f"🔢 Code: {activation_code}")
        print(f"{'='*50}\n")
        return True


class SMTPMailer:
    """SMTP email client for production use.

    Supports optional TLS and optional AUTH (for tools like MailHog).
    """

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        use_tls: bool = True,
    ) -> None:
        self.smtp_server: str = smtp_server
        self.smtp_port: int = smtp_port
        self.username: str = username
        self.password: str = password
        self.use_tls: bool = use_tls

    def send_activation_email(self, to_email: str, activation_code: str) -> bool:
        """Send activation email using SMTP."""
        try:

            # Create message
            message = MIMEMultipart(_subtype="alternative")
            message["Subject"] = "Activation de votre compte"
            # Use username as sender, or default for MailHog if username is empty
            message["From"] = self.username if self.username else "noreply@simpleauth.local"
            message["To"] = to_email

            # Create email content
            text_content: str = f"""
            Bonjour,

            Votre code d'activation est : {activation_code}

            Ce code expire dans 15 minutes.

            Cordialement,
            L'équipe Simple Auth
            """

            html_content: str = f"""
            <html>
              <body>
                <h2>Activation de votre compte</h2>
                <p>Bonjour,</p>
                <p>Votre code d'activation est : <strong>{activation_code}</strong></p>
                <p>Ce code expire dans 15 minutes.</p>
                <p>Cordialement,<br>L'équipe Simple Auth</p>
              </body>
            </html>
            """

            # Attach parts
            part1 = MIMEText(_text=text_content, _subtype="plain")
            part2 = MIMEText(_text=html_content, _subtype="html")
            message.attach(payload=part1)
            message.attach(payload=part2)

            # Send email
            with smtplib.SMTP(host=self.smtp_server, port=self.smtp_port) as server:
                # Optional TLS (MailHog typically doesn't support TLS)
                if self.use_tls:
                    try:
                        server.starttls()
                    except smtplib.SMTPException:
                        # If TLS fails (e.g., MailHog), continue without TLS
                        pass
                # Optional AUTH (MailHog doesn't require auth)
                if self.username and self.password:
                    server.login(user=self.username, password=self.password)
                server.send_message(msg=message)

            logger.info("Activation email sent successfully to %s", to_email)
            return True

        except (smtplib.SMTPException, ConnectionError, OSError) as e:
            logger.error("Failed to send activation email to %s: %s", to_email, str(e))
            return False


# Default mailer instance for development
Mailer = MockMailer
