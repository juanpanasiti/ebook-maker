import pytest
from unittest.mock import patch, MagicMock

from ebook_maker.ui.menu import prompt_note_action, display_note_metadata, prompt_edit_metadata
from ebook_maker.core.models import Note, NoteMetadata
from ebook_maker.core.settings import Settings

@patch('ebook_maker.ui.menu.questionary.select')
def test_prompt_note_action(mock_select, tmp_path):
    note_dir = tmp_path / "book"
    note_dir.mkdir()
    note = Note(path=note_dir, metadata=NoteMetadata(title="A title"))

    mock_ask = MagicMock()
    mock_ask.ask.return_value = "view"
    mock_select.return_value = mock_ask

    mock_settings = Settings(
        obsidian_root=tmp_path,
        epub_destination=tmp_path,
        kindle_email="test@kindle.com",
        smtp_user="user@gmail.com",
        smtp_password="pwd",
        _env_file=None
    )

    action = prompt_note_action(note, mock_settings)
    assert action == "view"
    mock_select.assert_called_once()


def test_display_note_metadata(capsys, tmp_path):
    note_dir = tmp_path / "book"
    note_dir.mkdir()
    note = Note(path=note_dir, metadata=NoteMetadata(title="A title", author="John Doe", language="en"))
    
    display_note_metadata(note)
    
    captured = capsys.readouterr()
    assert "A title" in captured.out
    assert "John Doe" in captured.out
    assert "en" in captured.out


@patch('ebook_maker.ui.menu.questionary.text')
@patch('ebook_maker.ui.menu.questionary.select')
@patch('ebook_maker.ui.menu.write_metadata')
def test_prompt_edit_metadata(mock_write, mock_select, mock_text, tmp_path):
    note_dir = tmp_path / "book"
    note_dir.mkdir()
    note = Note(path=note_dir, metadata=NoteMetadata(title="A title"))

    # Select title, change it, then select author, change it, then back
    mock_select_ask = MagicMock()
    mock_select_ask.ask.side_effect = ["title", "author", "back"]
    mock_select.return_value = mock_select_ask

    mock_text_ask = MagicMock()
    mock_text_ask.ask.side_effect = ["New Title", "New Author"]
    mock_text.return_value = mock_text_ask

    prompt_edit_metadata(note)
    
    assert note.metadata.title == "New Title"
    assert note.metadata.author == "New Author"
    assert mock_write.call_count == 2
