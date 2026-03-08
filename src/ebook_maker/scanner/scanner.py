import json
from pathlib import Path

from pydantic import ValidationError
from pydantic_core import to_json

from ebook_maker.core.models import Folder, Note, NoteMetadata, VaultEntry


def scan_vault(obsidian_root: Path, default_author: str = "Unknown Author", default_publisher: str | None = None) -> list[Note]:
    """Scans the Obsidian Vault and returns a list of Note objects."""
    notes: list[Note] = []
    
    # Recursively find all directories in the vault
    for directory in obsidian_root.rglob("*"):
        if directory.is_dir() and not directory.name.startswith("."):
            # Check if directory contains any markdown files
            if any(f.is_file() and f.suffix == ".md" for f in directory.iterdir()):
                note = process_note_directory(directory, default_author, default_publisher)
                notes.append(note)
                
    # Also check the root directory itself in case notes are there
    if any(f.is_file() and f.suffix == ".md" for f in obsidian_root.iterdir()):
        note = process_note_directory(obsidian_root, default_author, default_publisher)
        notes.append(note)
        
    return notes


def _has_notes_below(directory: Path) -> bool:
    """Check if any descendant directory contains markdown files."""
    for subdir in directory.rglob("*"):
        if subdir.is_dir() and not subdir.name.startswith("."):
            if any(f.is_file() and f.suffix == ".md" for f in subdir.iterdir()):
                return True
    return False


def scan_directory(directory: Path, default_author: str = "Unknown Author", default_publisher: str | None = None) -> list[VaultEntry]:
    """Scan a single directory level and return Notes and Folders.
    
    A direct child is a Note if it contains .md files.
    A direct child is a Folder if it doesn't contain .md files but has notes deeper in its hierarchy.
    """
    entries: list[VaultEntry] = []

    for child in sorted(directory.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue

        has_md = any(f.is_file() and f.suffix == ".md" for f in child.iterdir())

        if has_md:
            note = process_note_directory(child, default_author, default_publisher)
            entries.append(note)
        elif _has_notes_below(child):
            entries.append(Folder(path=child, name=child.name))

    return entries


def process_note_directory(directory: Path, default_author: str = "Unknown Author", default_publisher: str | None = None) -> Note:
    """Processes a single directory containing markdown files.
    Reads metadata.json or creates it if it doesn't exist.
    """
    metadata_path = directory / "metadata.json"
    
    # Check for default cover image
    default_cover = None
    for ext in [".png", ".jpg", ".jpeg"]:
        if (directory / f"cover{ext}").exists():
            default_cover = f"cover{ext}"
            break
    
    if metadata_path.exists():
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Apply defaults for missing or null values
                if data.get("title") is None:
                    data["title"] = directory.name
                    
                if data.get("author") is None:
                    data["author"] = default_author
                    
                if data.get("publisher") is None:
                    data["publisher"] = default_publisher
                    
                if data.get("language") is None:
                    data["language"] = "es"

                if data.get("finished") is None:
                    data["finished"] = False
                
                # If cover image is missing/null in metadata, check if a default file exists
                if data.get("cover_image") is None and default_cover:
                    data["cover_image"] = default_cover
                    
                metadata = NoteMetadata(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            # If the file is broken or schema is invalid, we fallback to a new one
            metadata = NoteMetadata(title=directory.name, author=default_author, publisher=default_publisher, cover_image=default_cover)
    else:
        # Create default metadata based on folder name
        metadata = NoteMetadata(title=directory.name, author=default_author, publisher=default_publisher, cover_image=default_cover)
        write_metadata(metadata_path, metadata)
        
    return Note(path=directory, metadata=metadata)


def write_metadata(path: Path, metadata: NoteMetadata) -> None:
    """Writes metadata to a JSON file."""
    # Write using pydantic's to_json to handle types correctly
    with open(path, "wb") as f:
        f.write(to_json(metadata, indent=4))
