from pathlib import Path
from datetime import datetime
import shutil

import pypandoc

import ebook_maker
from ebook_maker.core.models import Note
from ebook_maker.scanner.scanner import write_metadata


def get_epub_output_filename(note: Note) -> str:
    """Build output filename, prefixing draft notes for easy identification."""
    prefix = "" if note.metadata.finished else "[DRAFT] "
    return f"{prefix}{note.metadata.title}.epub"

def generate_epub(note: Note, output_dir: Path) -> Path:
    """
    Generates an EPUB from the provided Note object and saves it in output_dir.
    Returns the absolute path to the generated EPUB file.
    """
    # 1. Provide an auto-generated date as requested
    note.metadata.date = datetime.now().strftime("%Y-%m-%d")
    
    # Save the dynamically updated date back to metadata.json
    write_metadata(note.path / "metadata.json", note.metadata)

    # 2. Collect all markdown files to pass to pandoc in order
    md_files = [str(p) for p in note.markdown_files]
    if not md_files:
        raise ValueError(f"No markdown files found in the note '{note.metadata.title}'. Cannot generate EPUB.")

    output_filename = get_epub_output_filename(note)
    output_path = output_dir / output_filename

    # 3. Construct extra arguments for pandoc from metadata
    extra_args = []
    
    # Title
    extra_args.append(f"--metadata=title:{note.metadata.title}")
    # Author
    if note.metadata.author:
        for author in str(note.metadata.author).split(","):
            extra_args.append(f"--metadata=author:{author.strip()}")
    # Language
    if note.metadata.language:
        extra_args.append(f"--metadata=lang:{note.metadata.language}")
    # Date
    if note.metadata.date:
        extra_args.append(f"--metadata=date:{note.metadata.date}")
    # Description
    if note.metadata.description:
        extra_args.append(f"--metadata=description:{note.metadata.description}")
    # Publisher
    if note.metadata.publisher:
        extra_args.append(f"--metadata=publisher:{note.metadata.publisher}")
    # Identifier (UUID/ISBN)
    if note.metadata.identifier:
        extra_args.append(f"--metadata=identifier:{note.metadata.identifier}")

    # Generate Table of Contents up to h2
    extra_args.append("--toc")
    extra_args.append("--toc-depth=2")

    # Tell Pandoc where to find relative resources (images, etc.)
    extra_args.append(f"--resource-path={str(note.path)}")

    # Process Cover Image (Needs absolute path for pandoc or CWD execution)
    if note.metadata.cover_image:
        cover_path = note.path / note.metadata.cover_image
        if cover_path.exists():
            extra_args.append(f"--epub-cover-image={str(cover_path)}")

    # Add custom CSS styling
    css_path = Path(ebook_maker.__file__).parent / "assets" / "epub.css"
    if css_path.exists():
        extra_args.append(f"--css={str(css_path)}")

    # Add Lua filter for line numbers in code blocks
    lua_filter_path = Path(ebook_maker.__file__).parent / "assets" / "line-numbers.lua"
    if lua_filter_path.exists():
        extra_args.append(f"--lua-filter={str(lua_filter_path)}")

    # 4. Generate the actual EPUB using pypandoc
    # We use format 'markdown' explicitly and target 'epub'
    # By passing a list of files, pypandoc concatenates them
    try:
        pypandoc.convert_file(
            source_file=md_files,
            to="epub",
            outputfile=str(output_path),
            extra_args=extra_args
        )
    except Exception as e:
        raise RuntimeError(f"Pandoc conversion failed: {str(e)}") from e

    return output_path
