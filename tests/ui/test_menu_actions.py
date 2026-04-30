import pytest
from unittest.mock import patch, MagicMock

from ebook_maker.ui.menu import prompt_note_action, display_note_metadata, prompt_edit_metadata
from ebook_maker.core.models import Note, NoteMetadata
from ebook_maker.core.settings import Settings
from ebook_maker.converter.converter import get_epub_output_filename
from ebook_maker.converter.pdf_converter import get_pdf_output_filename


def _choice_values(choices):
    return [choice.value for choice in choices]


@patch('ebook_maker.ui.menu.questionary.select')
def test_prompt_note_action_orders_generation_and_metadata_actions(mock_select, tmp_path):
    note_dir = tmp_path / "book"
    note_dir.mkdir()
    (note_dir / "chapter.md").write_text("# Chapter 1\n")
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

    (mock_settings.epub_destination / get_epub_output_filename(note)).write_text("epub")
    (mock_settings.epub_destination / get_pdf_output_filename(note)).write_text("pdf")

    action = prompt_note_action(note, mock_settings)
    assert action == "view"
    mock_select.assert_called_once()

    choices = mock_select.call_args.kwargs["choices"]
    assert _choice_values(choices) == [
        "generate",
        "generate_pdf",
        "send",
        "open_location",
        "view",
        "edit",
        "back",
    ]


@patch('ebook_maker.ui.menu.questionary.select')
def test_prompt_note_action_hides_kindle_and_output_location_when_unavailable(mock_select, tmp_path):
    note_dir = tmp_path / "book"
    note_dir.mkdir()
    (note_dir / "chapter.md").write_text("# Chapter 1\n")
    note = Note(path=note_dir, metadata=NoteMetadata(title="A title"))

    mock_ask = MagicMock()
    mock_ask.ask.return_value = "view"
    mock_select.return_value = mock_ask

    mock_settings = Settings(
        obsidian_root=tmp_path,
        epub_destination=tmp_path,
        kindle_email=None,
        smtp_user=None,
        smtp_password=None,
        _env_file=None
    )

    action = prompt_note_action(note, mock_settings)
    assert action == "view"

    choices = mock_select.call_args.kwargs["choices"]
    assert _choice_values(choices) == [
        "generate",
        "generate_pdf",
        "view",
        "edit",
        "back",
    ]


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
