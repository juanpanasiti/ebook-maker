from unittest.mock import MagicMock, patch

from ebook_maker.core.models import Note, NoteMetadata
from ebook_maker.core.settings import Settings
from ebook_maker.main import main


@patch("ebook_maker.main.display_welcome_banner")
@patch("ebook_maker.main.display_no_notes_found")
@patch("ebook_maker.main.prompt_select_note")
@patch("ebook_maker.main.prompt_note_action")
@patch("ebook_maker.main.display_note_metadata")
@patch("ebook_maker.main.prompt_edit_metadata")
@patch("ebook_maker.main.generate_epub")
@patch("ebook_maker.main.generate_pdf")
@patch("ebook_maker.main.send_epub_to_kindle")
@patch("ebook_maker.main.scan_vault")
@patch("ebook_maker.main.scan_directory")
@patch("ebook_maker.main.get_settings")
@patch("subprocess.Popen")
def test_main_opens_shared_output_directory_and_keeps_other_actions_intact(
    mock_popen,
    mock_get_settings,
    mock_scan_directory,
    mock_scan_vault,
    mock_send_epub_to_kindle,
    mock_generate_pdf,
    mock_generate_epub,
    mock_prompt_edit_metadata,
    mock_display_note_metadata,
    mock_prompt_note_action,
    mock_prompt_select_note,
    mock_display_no_notes_found,
    mock_display_welcome_banner,
    tmp_path,
):
    note_dir = tmp_path / "book"
    note_dir.mkdir()
    (note_dir / "chapter.md").write_text("# Chapter 1\n")
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    note = Note(path=note_dir, metadata=NoteMetadata(title="A title"))

    settings = Settings(
        obsidian_root=tmp_path,
        epub_destination=output_dir,
        kindle_email=None,
        smtp_user=None,
        smtp_password=None,
        _env_file=None,
    )
    mock_get_settings.return_value = settings
    mock_scan_vault.return_value = [note]
    mock_scan_directory.return_value = [note]
    mock_prompt_select_note.side_effect = [note, note, note, "exit"]
    mock_prompt_note_action.side_effect = [
        "open_location",
        "back",
        "view",
        "back",
        "edit",
        "back",
    ]

    try:
        main()
    except SystemExit as exc:
        assert exc.code == 0

    mock_popen.assert_called_once_with(["xdg-open", str(output_dir)])
    assert mock_display_note_metadata.call_count == 1
    assert mock_prompt_edit_metadata.call_count == 1
    mock_generate_epub.assert_not_called()
    mock_generate_pdf.assert_not_called()
    mock_send_epub_to_kindle.assert_not_called()
    mock_display_no_notes_found.assert_not_called()
    mock_display_welcome_banner.assert_called()
