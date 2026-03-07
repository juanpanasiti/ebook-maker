from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class NoteMetadata(BaseModel):
    """Metadata for an EPUB generated from Obsidian notes."""
    title: str = Field(description="The title of the ebook")
    author: str = Field(default="Unknown Author", description="The author of the ebook")
    publisher: Optional[str] = Field(default=None, description="The publisher or organization")
    language: str = Field(default="es", description="The language of the ebook (e.g., 'en', 'es')")
    description: Optional[str] = Field(default=None, description="A brief summary of the ebook")
    date: Optional[str] = Field(default=None, description="Creation or publication date")
    identifier: Optional[str] = Field(default=None, description="ISBN or UUID")
    cover_image: Optional[str] = Field(default=None, description="Path to the cover image")


class Note(BaseModel):
    """Represents a notebook/folder to be converted into an EPUB."""
    path: Path = Field(description="The absolute path to the directory containing the markdown files")
    metadata: NoteMetadata = Field(description="The parsed metadata from metadata.json")
    
    @property
    def markdown_files(self) -> list[Path]:
        """Return a sorted list of all markdown files in the note directory."""
        # Simple sorting by name to ensure consistent ordering when pandoc compiles
        # If files start with numbers (e.g. 01-Intro.md, 02-Chapter.md), this works nicely.
        return sorted([f for f in self.path.iterdir() if f.is_file() and f.suffix == ".md"])
