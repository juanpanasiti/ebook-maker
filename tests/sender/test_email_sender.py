import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from ebook_maker.core.settings import Settings
from ebook_maker.sender.email_sender import send_epub_to_kindle, EmailConfigurationError

@patch("ebook_maker.sender.email_sender.smtplib.SMTP")
def test_send_epub_success(mock_smtp_class, tmp_path):
    mock_smtp_instance = mock_smtp_class.return_value.__enter__.return_value

    epub_file = tmp_path / "test.epub"
    epub_file.write_bytes(b"dummy data")

    settings = Settings(
        obsidian_root=tmp_path,
        epub_destination=tmp_path,
        kindle_email="kindle@kindle.com",
        smtp_user="me@gmail.com",
        smtp_password="password123",
        _env_file=None
    )

    send_epub_to_kindle(epub_file, settings)

    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with("me@gmail.com", "password123")
    mock_smtp_instance.send_message.assert_called_once()
    
    # Assert attachment format
    args, kwargs = mock_smtp_instance.send_message.call_args
    msg = args[0]
    assert msg['To'] == "kindle@kindle.com"
    assert len(msg.get_payload()) > 0  # It has parts now

def test_send_epub_missing_config(tmp_path):
    epub_file = tmp_path / "test.epub"
    epub_file.write_bytes(b"dummy data")

    settings = Settings(
        obsidian_root=tmp_path,
        epub_destination=tmp_path,
        kindle_email=None,  # Missing
        smtp_user="me@gmail.com",
        smtp_password="password123",
        _env_file=None
    )

    with pytest.raises(EmailConfigurationError, match="Missing email configuration"):
        send_epub_to_kindle(epub_file, settings)

def test_send_epub_missing_file(tmp_path):
    epub_file = tmp_path / "non_existent.epub"

    settings = Settings(
        obsidian_root=tmp_path,
        epub_destination=tmp_path,
        kindle_email="kindle@kindle.com",
        smtp_user="me@gmail.com",
        smtp_password="password123",
        _env_file=None
    )

    with pytest.raises(FileNotFoundError, match="EPUB file not found"):
        send_epub_to_kindle(epub_file, settings)

@patch("ebook_maker.sender.email_sender.smtplib.SMTP")
def test_send_epub_smtp_failure(mock_smtp_class, tmp_path):
    mock_smtp_instance = mock_smtp_class.return_value.__enter__.return_value
    mock_smtp_instance.login.side_effect = Exception("SMTP Auth Failed")

    epub_file = tmp_path / "test.epub"
    epub_file.write_bytes(b"dummy data")

    settings = Settings(
        obsidian_root=tmp_path,
        epub_destination=tmp_path,
        kindle_email="kindle@kindle.com",
        smtp_user="me@gmail.com",
        smtp_password="password123",
        _env_file=None
    )

    with pytest.raises(RuntimeError, match="Failed to send email via SMTP: SMTP Auth Failed"):
        send_epub_to_kindle(epub_file, settings)
