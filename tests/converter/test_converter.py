import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime

from ebook_maker.core.models import Note, NoteMetadata
from ebook_maker.converter.converter import generate_epub

@patch("ebook_maker.converter.converter.pypandoc.convert_file")
@patch("ebook_maker.converter.converter.write_metadata")
def test_generate_epub_success(mock_write, mock_pandoc, tmp_path):
    note_dir = tmp_path / "book"
    note_dir.mkdir()
    
    # We need at least one markdown file to avoid ValueError
    md_file = note_dir / "chapter.md"
    md_file.write_text("Hello World!")
    
    # Optional cover image
    cover_file = note_dir / "cover.png"
    cover_file.touch()

    note = Note(
        path=note_dir, 
        metadata=NoteMetadata(
            title="A title",
            author="Author One, Author Two",
            language="en",
            publisher="My Publisher",
            description="A test description",
            identifier="test-identifier",
            cover_image="cover.png"
        )
    )

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Call the generator
    out_path = generate_epub(note, output_dir)
    
    assert out_path == output_dir / "A title.epub"
    
    # Date should be automatically updated to today
    today_str = datetime.now().strftime("%Y-%m-%d")
    assert note.metadata.date == today_str
    
    mock_write.assert_called_once()
    
    # Verify pandoc was called correctly
    mock_pandoc.assert_called_once()
    args, kwargs = mock_pandoc.call_args
    
    assert kwargs["to"] == "epub"
    assert kwargs["outputfile"] == str(out_path)
    assert [str(md_file)] == kwargs["source_file"]
    
    # Check extra_args composition
    extra_args = kwargs["extra_args"]
    assert "--metadata=title:A title" in extra_args
    assert "--metadata=author:Author One" in extra_args
    assert "--metadata=author:Author Two" in extra_args
    assert "--metadata=lang:en" in extra_args
    assert "--metadata=publisher:My Publisher" in extra_args
    assert f"--metadata=date:{today_str}" in extra_args
    assert "--metadata=description:A test description" in extra_args
    assert "--metadata=identifier:test-identifier" in extra_args
    assert f"--epub-cover-image={str(cover_file)}" in extra_args


def test_generate_epub_no_markdown_files(tmp_path):
    note_dir = tmp_path / "book"
    note_dir.mkdir()
    
    # NO markdown files created here!

    note = Note(path=note_dir, metadata=NoteMetadata(title="Empty Book"))
    output_dir = tmp_path / "output"

    with pytest.raises(ValueError, match="No markdown files found"):
        generate_epub(note, output_dir)


@patch("ebook_maker.converter.converter.pypandoc.convert_file")
@patch("ebook_maker.converter.converter.write_metadata")
def test_generate_epub_pandoc_failure(mock_write, mock_pandoc, tmp_path):
    note_dir = tmp_path / "book"
    note_dir.mkdir()
    (note_dir / "chap.md").touch()
    note = Note(path=note_dir, metadata=NoteMetadata(title="Failing Book"))

    output_dir = tmp_path / "output"

    # Force a failure
    mock_pandoc.side_effect = RuntimeError("Pandoc error")

    with pytest.raises(RuntimeError, match="Pandoc conversion failed: Pandoc error"):
        generate_epub(note, output_dir)
