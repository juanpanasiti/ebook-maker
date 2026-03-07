import pytest

from ebook_maker.core.models import Note, NoteMetadata


def test_note_metadata_defaults():
    """Test correctly falling back to defaults for optional fields."""
    metadata = NoteMetadata(title="My Great Book")
    assert metadata.title == "My Great Book"
    assert metadata.author == "Unknown Author"
    assert metadata.language == "es"
    assert metadata.cover_image is None


def test_note_markdown_files_property(tmp_path):
    """Test Note dynamically lists its markdown files in order."""
    # Create mock folder and files
    note_dir = tmp_path / "My Note"
    note_dir.mkdir()
    
    file2 = note_dir / "02-Chapter 2.md"
    file2.write_text("content")
    
    file1 = note_dir / "01-Introduction.md"
    file1.write_text("intro")
    
    # Ignore this, not md
    file_txt = note_dir / "random.txt"
    file_txt.write_text("text")

    metadata = NoteMetadata(title="My Note")
    note = Note(path=note_dir, metadata=metadata)

    # Note that it ignores .txt and sorts by filename
    assert len(note.markdown_files) == 2
    assert note.markdown_files[0] == file1
    assert note.markdown_files[1] == file2
