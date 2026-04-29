# Architecture

## System Overview
Ebook Maker is a terminal CLI for turning Obsidian note folders into distributable ebooks. The package is installed globally with `uv tool install .`, which exposes the `ebook-maker` command defined in `pyproject.toml`. For local development, the same application can be started with `./run.sh` or `uv run python -m ebook_maker.main`.

At runtime, the CLI loads configuration, scans the Obsidian vault for note directories, and enters an interactive loop where the user can inspect metadata, edit metadata, generate EPUB files, generate PDF files, open output folders, or send an EPUB to Kindle via SMTP.

## Tech Stack
- Language: Python 3.14+
- Dependency and environment management: `uv`
- Settings and validation: `pydantic` and `pydantic-settings`
- EPUB generation: `pypandoc` with Pandoc
- PDF generation: `pypandoc` with Pandoc plus `weasyprint`
- CLI interaction: `rich` and `questionary`
- Environment loading: `python-dotenv` through Pydantic settings configuration
- Testing: `pytest` and `pytest-cov`

## Project Structure
- `src/ebook_maker/main.py`: application entry point and interactive control loop.
- `src/ebook_maker/__init__.py`: re-exports `main` for the console script entry point.
- `src/ebook_maker/core/`: Pydantic domain models and settings loading.
- `src/ebook_maker/scanner/`: vault scanning, note detection, and `metadata.json` read/write logic.
- `src/ebook_maker/converter/`: EPUB and PDF conversion pipelines.
- `src/ebook_maker/sender/`: SMTP email delivery for Kindle uploads.
- `src/ebook_maker/ui/`: Rich console output and Questionary menus.
- `src/ebook_maker/assets/`: CSS and Lua assets packaged with the distribution.
- `tests/`: mirrored test suite for the package modules.
- Top-level scripts: `run.sh` for local execution, `test.sh` for the test run, and `install.sh` for global installation plus optional config copying.

## Core Logic Flow
1. The console script resolves to `ebook_maker:main`, which imports and runs `ebook_maker.main.main`.
2. `main()` prints the welcome banner and loads configuration through `get_settings()`.
3. If settings validation fails, the program prints a configuration error and exits with status code 1.
4. The application scans the configured Obsidian root with `scan_vault()` to build the initial list of notes.
5. Inside the navigation loop, `scan_directory()` loads the current folder view and returns either `Note` objects or navigable `Folder` objects.
6. `prompt_select_note()` lets the user choose a note, move back, or exit.
7. For a selected note, `prompt_note_action()` exposes metadata viewing, metadata editing, EPUB generation, PDF generation, output-folder opening, and Kindle sending when SMTP settings are complete.
8. `generate_epub()` persists the current date into `metadata.json`, assembles Pandoc arguments, and writes an EPUB to the configured destination.
9. `generate_pdf()` persists the current date into `metadata.json`, converts Markdown to HTML5, optionally injects a cover page, and renders a PDF with WeasyPrint.
10. `send_epub_to_kindle()` attaches the EPUB to an email message and delivers it through SMTP when the Kindle settings are present.

## Testing Strategy
The project uses `pytest` for the test suite and `pytest-cov` for coverage reporting. The canonical local test command is `./test.sh`, which runs `uv run pytest tests/ --cov=src/ebook_maker --cov-report=term-missing`.

The test layout mirrors the package structure under `tests/`, and external integrations are mocked rather than executed against real services. Pandoc, WeasyPrint, SMTP, and interactive CLI prompts are covered with mocks in the relevant tests.

## Invariants
- Domain data is modeled with Pydantic classes in `src/ebook_maker/core/models.py`.
- Application configuration is loaded only through `src/ebook_maker/core/settings.py`.
- A note is a directory that contains at least one `.md` file.
- Hidden directories are ignored by the scanner.
- `metadata.json` is created automatically when missing and is repaired with defaults when invalid data is encountered.
- `Note.markdown_files` is sorted by filename to keep Pandoc input order stable.
- Output filenames use a `[DRAFT]` prefix when `finished` is false.
- EPUB generation uses Pandoc directly with project CSS and Lua filters.
- PDF generation uses Pandoc to produce HTML5 and WeasyPrint to render the final PDF.
- Kindle sending is only exposed when `kindle_email`, `smtp_user`, and `smtp_password` are all present.
- Packaged assets are included through the `uv_build` module-data configuration.