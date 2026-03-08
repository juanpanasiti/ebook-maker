import json
from pathlib import Path

from ebook_maker.core.models import Folder, Note, NoteMetadata
from ebook_maker.scanner.scanner import scan_vault, scan_directory


def test_scan_vault_finds_notes(tmp_path):
    """Test that the scanner recursively finds directories with .md files."""
    obsidian_root = tmp_path / "obsidian"
    obsidian_root.mkdir()

    # Create a note directory (should be found)
    note_dir = obsidian_root / "My First Book"
    note_dir.mkdir()
    (note_dir / "chapter1.md").write_text("# Chapter 1")

    # Create a directory without .md files (should be ignored)
    empty_dir = obsidian_root / "Attachments"
    empty_dir.mkdir()
    (empty_dir / "image.png").touch()
    
    # Create a nested note
    nested_dir = obsidian_root / "Projects" / "Ebook"
    nested_dir.mkdir(parents=True)
    (nested_dir / "draft.md").write_text("draft content")
    
    # Hidden folder (should be ignored)
    hidden_dir = obsidian_root / ".obsidian"
    hidden_dir.mkdir()
    (hidden_dir / "workspace.md").write_text("{}")
    
    notes = scan_vault(obsidian_root)

    # Sort to assure predictable assertions
    notes.sort(key=lambda n: n.path.name)
    
    assert len(notes) == 2
    assert notes[0].path == nested_dir
    assert notes[1].path == note_dir


def test_scan_vault_creates_metadata_if_missing(tmp_path):
    """Test that scanner creates a metadata.json if it doesn't exist."""
    obsidian_root = tmp_path / "obsidian"
    obsidian_root.mkdir()

    note_dir = obsidian_root / "Book Without Meta"
    note_dir.mkdir()
    (note_dir / "intro.md").write_text("# Intro")

    # Initially, no metadata.json
    assert not (note_dir / "metadata.json").exists()

    notes = scan_vault(obsidian_root)
    assert len(notes) == 1
    
    note = notes[0]
    
    # It should have dynamically created a metadata file using the folder name
    assert note.metadata.title == "Book Without Meta"
    assert (note_dir / "metadata.json").exists()


def test_scan_vault_reads_existing_metadata(tmp_path):
    """Test that scanner reads existing metadata.json."""
    obsidian_root = tmp_path / "obsidian"
    obsidian_root.mkdir()

    note_dir = obsidian_root / "Known Book"
    note_dir.mkdir()
    (note_dir / "intro.md").write_text("# Intro")

    # Create an existing metadata.json
    meta = NoteMetadata(title="Custom Title", author="Juan Panasiti", language="en")
    (note_dir / "metadata.json").write_text(meta.model_dump_json())

    notes = scan_vault(obsidian_root)
    assert len(notes) == 1
    note = notes[0]

    # It should reflect the custom data
    assert note.metadata.title == "Custom Title"
    assert note.metadata.author == "Juan Panasiti"


def test_scan_vault_handles_invalid_metadata(tmp_path):
    """Test that scanner handles invalid metadata.json by gracefully defaulting."""
    obsidian_root = tmp_path / "obsidian"
    obsidian_root.mkdir()

    note_dir = obsidian_root / "Broken Meta Book"
    note_dir.mkdir()
    (note_dir / "chap1.md").write_text("# Chap 1")

    # Write broken JSON
    (note_dir / "metadata.json").write_text("{broken json...")

    notes = scan_vault(obsidian_root)
    assert len(notes) == 1
    note = notes[0]

    # Default fallback title due to Exception
    assert note.metadata.title == "Broken Meta Book"


def test_scan_vault_root_directory(tmp_path):
    """Test that scanner processes the root directory if it has .md files."""
    obsidian_root = tmp_path / "obsidian"
    obsidian_root.mkdir()

    # Put a markdown file directly in root
    (obsidian_root / "standalone.md").write_text("Hello")
    
    notes = scan_vault(obsidian_root)
    
    assert len(notes) == 1
    assert notes[0].path == obsidian_root
    assert notes[0].metadata.title == "obsidian"


def test_scan_vault_detects_default_cover_and_author(tmp_path):
    """Test that scanner auto populates cover image and default author."""
    obsidian_root = tmp_path / "obsidian"
    obsidian_root.mkdir()

    note_dir = obsidian_root / "Book With Cover"
    note_dir.mkdir()
    (note_dir / "intro.md").write_text("# Intro")
    
    # Create cover.png
    (note_dir / "cover.png").touch()

    notes = scan_vault(obsidian_root, default_author="Test Author")
    assert len(notes) == 1
    
    note = notes[0]
    
    # Should use the injected default author
    assert note.metadata.author == "Test Author"
    # Should automatically link to cover.png
    assert note.metadata.cover_image == "cover.png"


def test_scan_directory_returns_notes_and_folders(tmp_path):
    """Test that scan_directory returns Notes for dirs with .md and Folders for dirs with nested notes."""
    root = tmp_path / "vault"
    root.mkdir()

    # A: has .md files → Note
    a = root / "A"
    a.mkdir()
    (a / "chapter.md").write_text("# A")

    # B: has .md files → Note
    b = root / "B"
    b.mkdir()
    (b / "chapter.md").write_text("# B")

    # C: no .md, but has subfolders with .md → Folder
    c = root / "C"
    c.mkdir()
    d = c / "D"
    d.mkdir()
    (d / "chapter.md").write_text("# D")

    entries = scan_directory(root)

    assert len(entries) == 3
    assert isinstance(entries[0], Note)  # A
    assert isinstance(entries[1], Note)  # B
    assert isinstance(entries[2], Folder)  # C
    assert entries[2].name == "C"


def test_scan_directory_ignores_empty_dirs(tmp_path):
    """Test that directories without notes anywhere below are skipped."""
    root = tmp_path / "vault"
    root.mkdir()

    note_dir = root / "Book"
    note_dir.mkdir()
    (note_dir / "chapter.md").write_text("# Book")

    empty_dir = root / "Empty"
    empty_dir.mkdir()

    entries = scan_directory(root)

    assert len(entries) == 1
    assert isinstance(entries[0], Note)


def test_scan_directory_ignores_hidden_dirs(tmp_path):
    """Test that hidden directories are skipped."""
    root = tmp_path / "vault"
    root.mkdir()

    hidden = root / ".obsidian"
    hidden.mkdir()
    (hidden / "note.md").write_text("hidden")

    visible = root / "Book"
    visible.mkdir()
    (visible / "chapter.md").write_text("# Book")

    entries = scan_directory(root)

    assert len(entries) == 1
    assert isinstance(entries[0], Note)


def test_scan_directory_navigates_into_folder(tmp_path):
    """Test that scanning inside a Folder returns its nested Notes/Folders."""
    root = tmp_path / "vault"
    root.mkdir()

    category = root / "Category"
    category.mkdir()

    course1 = category / "Course1"
    course1.mkdir()
    (course1 / "lesson.md").write_text("# Lesson")

    course2 = category / "Course2"
    course2.mkdir()
    (course2 / "lesson.md").write_text("# Lesson")

    # First level: Category is a Folder
    entries = scan_directory(root)
    assert len(entries) == 1
    assert isinstance(entries[0], Folder)

    # Drill into Category: Course1 and Course2 are Notes
    sub_entries = scan_directory(entries[0].path)
    assert len(sub_entries) == 2
    assert all(isinstance(e, Note) for e in sub_entries)
