from pathlib import Path
from datetime import datetime
import base64
import mimetypes

import pypandoc
from weasyprint import HTML, CSS

import ebook_maker
from ebook_maker.core.models import Note
from ebook_maker.scanner.scanner import write_metadata


def get_pdf_output_filename(note: Note) -> str:
    """Build output filename, prefixing draft notes for easy identification."""
    prefix = "" if note.metadata.finished else "[DRAFT] "
    return f"{prefix}{note.metadata.title}.pdf"


def _build_cover_html(cover_path: Path) -> str:
    """
    Returns an HTML snippet for a full-page cover image.
    Embeds the image as base64 to avoid path-resolution issues in WeasyPrint.
    """
    mime_type, _ = mimetypes.guess_type(str(cover_path))
    mime_type = mime_type or "image/jpeg"

    with open(cover_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    data_uri = f"data:{mime_type};base64,{encoded}"

    return f"""
<div class="cover-page">
    <img class="cover-image" src="{data_uri}" alt="Cover" />
</div>
"""


def _build_cover_first_page_override_css() -> str:
    """
    Forces the very first page (cover) to have zero margins and no footer/header
    artifacts, avoiding default page-margin bleed on some WeasyPrint layouts.
    """
    return """
<style>
@page :first {
    size: A4;
    margin: 0;
    @bottom-center { content: none; }
    @bottom-left   { content: none; }
    @top-center    { content: none; }
}
</style>
"""


def _build_metadata_block(note: Note) -> str:
    """Returns an HTML comment block with document metadata (for debugging / archiving)."""
    meta = note.metadata
    lines = [
        "<!-- PDF Metadata",
        f"  Title     : {meta.title}",
        f"  Author    : {meta.author}",
        f"  Language  : {meta.language}",
    ]
    if meta.date:
        lines.append(f"  Date      : {meta.date}")
    if meta.publisher:
        lines.append(f"  Publisher : {meta.publisher}")
    if meta.description:
        lines.append(f"  Desc      : {meta.description}")
    lines.append("-->")
    return "\n".join(lines)


def generate_pdf(note: Note, output_dir: Path) -> Path:
    """
    Generates an A4 PDF from the provided Note object and saves it in output_dir.
    
    Pipeline:
      Markdown files → pandoc (→ HTML5) → WeasyPrint (→ PDF)

    Returns the absolute path to the generated PDF file.
    """
    # 1. Auto-generate date and persist it
    note.metadata.date = datetime.now().strftime("%Y-%m-%d")
    write_metadata(note.path / "metadata.json", note.metadata)

    # 2. Collect markdown files
    md_files = [str(p) for p in note.markdown_files]
    if not md_files:
        raise ValueError(
            f"No markdown files found in note '{note.metadata.title}'. Cannot generate PDF."
        )

    output_filename = get_pdf_output_filename(note)
    output_path = output_dir / output_filename

    # 3. Build extra args for pandoc (HTML output)
    extra_args = [
        "--from=markdown+markdown_in_html_blocks",  # Ensure markdown translates inside <div align="right">
        "--standalone",
        "--highlight-style=tango", # Inyecta CSS del tema Tango nativo de Pandoc (mejores colores)
        "--toc",
        "--toc-depth=2",
        f"--resource-path={str(note.path)}",
        "--embed-resources",          # inline images / CSS into the HTML
    ]

    # Metadata
    extra_args.append(f"--metadata=title:{note.metadata.title}")
    if note.metadata.author:
        for author in str(note.metadata.author).split(","):
            extra_args.append(f"--metadata=author:{author.strip()}")
    if note.metadata.language:
        extra_args.append(f"--metadata=lang:{note.metadata.language}")
    if note.metadata.date:
        extra_args.append(f"--metadata=date:{note.metadata.date}")
    if note.metadata.description:
        extra_args.append(f"--metadata=description:{note.metadata.description}")
    if note.metadata.publisher:
        extra_args.append(f"--metadata=publisher:{note.metadata.publisher}")
    if note.metadata.identifier:
        extra_args.append(f"--metadata=identifier:{note.metadata.identifier}")

    # Lua filter for line numbers in code blocks (same as EPUB)
    lua_filter_path = Path(ebook_maker.__file__).parent / "assets" / "line-numbers.lua"
    if lua_filter_path.exists():
        extra_args.append(f"--lua-filter={str(lua_filter_path)}")

    # Add Lua filter for Obsidian Callouts
    callout_lua = Path(ebook_maker.__file__).parent / "assets" / "obsidian-callouts.lua"
    if callout_lua.exists():
        extra_args.append(f"--lua-filter={str(callout_lua)}")

    # Add Lua filter for unsupported syntax aliases (e.g. rego -> go)
    syntax_alias_lua = Path(ebook_maker.__file__).parent / "assets" / "syntax-alias.lua"
    if syntax_alias_lua.exists():
        extra_args.append(f"--lua-filter={str(syntax_alias_lua)}")

    # 4. Convert Markdown → HTML via pandoc
    try:
        html_body: str = pypandoc.convert_file(
            source_file=md_files,
            to="html5",
            extra_args=extra_args,
        )
    except Exception as e:
        raise RuntimeError(f"Pandoc conversion to HTML failed: {str(e)}") from e

    # 5. Prepend full-page cover if available
    cover_prefix = ""
    if note.metadata.cover_image:
        cover_path = note.path / note.metadata.cover_image
        if cover_path.exists():
            cover_prefix = _build_cover_html(cover_path)
            cover_page_override_css = _build_cover_first_page_override_css()
            if "<head>" in html_body:
                html_body = html_body.replace("<head>", f"<head>\n{cover_page_override_css}", 1)

    # 6. Inject cover before <body> content
    #    pandoc --standalone produces a full HTML document; we insert the cover
    #    right after the opening <body> tag so it becomes the very first page.
    if cover_prefix:
        if "<body>" in html_body:
            html_body = html_body.replace("<body>", f"<body>\n{cover_prefix}", 1)
        else:
            # Fallback: prepend to the document
            html_body = cover_prefix + html_body

    # 7. Load our PDF-specific CSS
    css_path = Path(ebook_maker.__file__).parent / "assets" / "pdf.css"
    stylesheets = []
    if css_path.exists():
        stylesheets.append(CSS(filename=str(css_path)))

    # 8. Render to PDF with WeasyPrint
    #    base_url = note.path so that any remaining relative URLs resolve correctly
    try:
        document = HTML(
            string=html_body,
            base_url=str(note.path),
        )
        document.write_pdf(
            target=str(output_path),
            stylesheets=stylesheets,
        )
    except Exception as e:
        raise RuntimeError(f"WeasyPrint PDF rendering failed: {str(e)}") from e

    return output_path
