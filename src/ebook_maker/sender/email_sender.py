import smtplib
from pathlib import Path
from email.message import EmailMessage

from ebook_maker.core.settings import Settings

class EmailConfigurationError(Exception):
    pass

def send_epub_to_kindle(epub_path: Path, settings: Settings) -> None:
    """
    Sends the generated EPUB file to a Kindle device via email using SMTP.
    Requires Kindle Email, SMTP User and SMTP Password to be set in settings.
    """
    if not settings.kindle_email or not settings.smtp_user or not settings.smtp_password:
        raise EmailConfigurationError("Missing email configuration. Please check your .env file.")

    if not epub_path.exists():
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")

    # Build the email
    msg = EmailMessage()
    msg['Subject'] = 'Sent from Ebook Maker'
    msg['From'] = settings.smtp_user
    msg['To'] = settings.kindle_email
    
    # Empty body is fine for Amazon Kindle Personal Document Service
    msg.set_content("Please find the attached EPUB document.")

    # Read and attach the EPUB file
    with open(epub_path, 'rb') as f:
        epub_data = f.read()
        
    msg.add_attachment(
        epub_data, 
        maintype='application', 
        subtype='epub+zip', 
        filename=epub_path.name
    )

    # Connect to the SMTP Server and send
    try:
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.ehlo()
            server.starttls()  # Secure the connection
            server.ehlo()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
    except Exception as e:
        raise RuntimeError(f"Failed to send email via SMTP: {str(e)}") from e
