# Spec-Driven Development (SDD) Principles

This project follows **Spec-Driven Development**. Before proposing, suggesting, or writing any code, you MUST:
1. **Read mandatory artifacts:** Consult `architecture.md` and `.openspec/config.yaml` to understand the current system state and constraints.
2. **Validate against specs:** If a change request contradicts the architecture or existing specs, refuse to proceed. Explain why and ask for clarification.
3. **No vibe coding:** Never guess at architectural decisions, assume module placement, or invent patterns not already in the codebase.
4. **Demand clarity:** If you lack sufficient context to implement a request, stop immediately and ask focused questions. Do not fill gaps with assumptions.

---

# Project Context
This project is a terminal application (CLI) for converting Obsidian Markdown notes into EPUB and PDF ebooks.
The primary audience is people who write documentation, courses, or books in Obsidian and want to generate files ready for e-readers (especially Kindle) with good formatting, navigation, and metadata.
The goal is to maintain a clear console user experience, robust conversions, and simple `.env`-based configuration.

**For architectural details, see:** [architecture.md](../architecture.md)
**For OpenSpec workflow rules, see:** [.openspec/config.yaml](../openspec/config.yaml)

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

## Architecture & Layering
- **Modeling:** All domain data (notes, metadata, folders) must be represented using Pydantic models in `core/models.py`.
- **Configuration:** All environment loading must go through `core/settings.py` (do not read `os.environ` directly from business logic).
- **Conversions:** EPUB/PDF generation must live in `converter/` and must not be mixed with UI or interactive prompts.
- **Scanning:** Vault note and folder detection must live in `scanner/`.
- **Email sending:** SMTP/Kindle logic must remain encapsulated in `sender/email_sender.py`.
- **Separation:** Always respect the layered separation: `core/`, `scanner/`, `converter/`, `sender/`, `ui/`. Do not cross-pollinate concerns.

## Testing & Quality
- **Testing:** Every new module must include tests in `tests/`, following the same folder structure as `src/ebook_maker/`.
- **Mocks:** For external integrations (Pandoc, SMTP, CLI interaction), use mocks in tests instead of relying on real services.
- **Coverage:** Refer to `.openspec/config.yaml` scripts for the test command: `uv run pytest tests/ --cov=src/ebook_maker --cov-report=term-missing`.
- **Regression:** If you change functional behavior, suggest or add regression tests in the corresponding module.
- **Comments:** Comment the *why* for non-obvious logic; avoid redundant comments that describe the obvious.

## Dependency & Environment
- **Package Manager:** Only use `uv` for managing dependencies and running commands. Never suggest `pip`, `poetry`, `conda`, or other package managers.
- **Commands:** All development scripts must use `uv run` or defined scripts in `.openspec/config.yaml`. Examples: `uv sync`, `uv run pytest`.
- **Constraints:** Do not add dependencies without justifying why existing libraries cannot solve the problem.

## Spec-Driven Validation
- **Refuse contradictions:** If a request violates `architecture.md` or existing design decisions, refuse politely and explain.
- **Ask for specs:** If unsure whether a change is appropriate, ask the user to clarify requirements or point to relevant specs.
- **Document decisions:** Significant changes should be captured in OpenSpec artifacts (proposal, design, specs, tasks) before implementation.

# Base Prompts (Assistant Behavior)

## SDD Mindset
- **Architecture-first:** Before writing any code, ensure you understand how it fits into the system described in `architecture.md`.
- **Spec validation:** Check `.openspec/config.yaml` and any active OpenSpec artifacts for context, constraints, and decisions.
- **Honesty:** If you lack sufficient information to make a design decision, ask focused questions instead of guessing.
- **Refusal:** If a request contradicts established architecture or design, refuse clearly and explain the conflict.

## Development Practices
- When suggesting refactors, prioritize readability and maintainability of the CLI flow.
- Before proposing a new dependency, prioritize solving it with the standard library or libraries already present in the project.
- Respect the project's layered separation: `core/`, `scanner/`, `converter/`, `sender/`, `ui/`.
- If you change functional behavior, suggest or add regression tests in the corresponding module.
- Keep compatibility with the current execution flow (`ebook-maker`, `./run.sh`, `uv run ...`).

## Communication
- Always respond in English, with a technical and direct tone.
- When unsure, ask specific questions: "Which module should this logic belong to?" rather than guessing.
- If a request is vague, ask for clarification pointing to relevant parts of `architecture.md` or existing code.
