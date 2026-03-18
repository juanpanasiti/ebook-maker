import sys
from unittest.mock import MagicMock, patch

import pytest

from ebook_maker.core.models import Note, NoteMetadata
from ebook_maker.main import main
from ebook_maker.ui.menu import display_no_notes_found, display_welcome_banner


def test_display_welcome_banner(capsys):
    """Test the welcome banner avoids errors."""
    display_welcome_banner()
    captured = capsys.readouterr()
    assert "Obsidian to EPUB & PDF Maker" in captured.out


@patch("sys.exit")
def test_display_no_notes_found(mock_exit, capsys):
    """Test exit when no notes are found."""
    display_no_notes_found()
    mock_exit.assert_called_once_with(0)
    
    captured = capsys.readouterr()
    assert "No notes found" in captured.out


@patch("ebook_maker.ui.menu.questionary.select")
def test_prompt_select_note(mock_select, tmp_path):
    """Test Questionary prompt logic."""
    from ebook_maker.ui.menu import prompt_select_note
    from pathlib import Path
    
    note_dir = tmp_path / "book"
    note_dir.mkdir()

    note = Note(path=note_dir, metadata=NoteMetadata(title="A title"))
    
    # Mock return value of questionary.select().ask()
    mock_ask = MagicMock()
    mock_ask.ask.return_value = note
    mock_select.return_value = mock_ask

    selected = prompt_select_note([note])

    assert selected == note
    mock_select.assert_called_once()
