# Project Context
This project is a terminal application (CLI) for converting Obsidian Markdown notes into EPUB and PDF ebooks.
The primary audience is people who write documentation, courses, or books in Obsidian and want to generate files ready for e-readers (especially Kindle) with good formatting, navigation, and metadata.
The goal is to maintain a clear console user experience, robust conversions, and simple `.env`-based configuration.

# Tech Stack
- Language: Python 3.14+
- CLI Interface: Rich, Questionary
- EPUB Conversion: Pandoc (via pypandoc) + custom CSS + Lua filter
- PDF Conversion: WeasyPrint + custom CSS
- Configuration: python-dotenv, pydantic-settings
- Modeling and Validation: Pydantic v2
- Testing: pytest, unittest.mock
- Build/packaging: pyproject.toml + uv_build
- Execution and installation: uv (`uv run`, `uv tool install`)

# Code Conventions (Code Style)
- Use `snake_case` for variables, functions, and modules.
- Use `PascalCase` for classes and models.
- Use `UPPER_SNAKE_CASE` for module-level constants.
- Prefer modern Python type hints (`str | None`, `list[Path]`) over `typing.Optional`/`typing.List`, except where necessary.
- Prefer small, focused functions with a single responsibility.
- Centralize data and settings validation in Pydantic models.
- Handle errors with clear messages for CLI users and do not hide relevant exceptions.

# Specific Rules
- **Modeling:** All domain data (notes, metadata, folders) must be represented using Pydantic models in `core/models.py`.
- **Configuration:** All environment loading must go through `core/settings.py` (do not read `os.environ` directly from business logic).
- **Conversions:** EPUB/PDF generation must live in `converter/` and must not be mixed with UI or interactive prompts.
- **Scanning:** Vault note and folder detection must live in `scanner/`.
- **Email sending:** SMTP/Kindle logic must remain encapsulated in `sender/email_sender.py`.
- **Testing:** Every new module must include tests in `tests/`, following the same folder structure as `src/ebook_maker/`.
- **Mocks:** For external integrations (Pandoc, SMTP, CLI interaction), use mocks in tests instead of relying on real services.
- **Comments:** Comment the *why* for non-obvious logic; avoid redundant comments that describe the obvious.

# Base Prompts (Assistant Behavior)
- When suggesting refactors, prioritize readability and maintainability of the CLI flow.
- Before proposing a new dependency, prioritize solving it with the standard library or libraries already present in the project.
- Respect the project's layered separation: `core/`, `scanner/`, `converter/`, `sender/`, `ui/`.
- If you change functional behavior, suggest or add regression tests in the corresponding module.
- Keep compatibility with the current execution flow (`ebook-maker`, `./run.sh`, `uv run ...`).
- Always respond in English, with a technical and direct tone.
