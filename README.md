# Ebook Maker

Ebook Maker is a terminal application built in Python that converts Obsidian notes into EPUB format using Pandoc. It provides an interactive and colorful command-line interface to scan your Obsidian vault for notes, manage their metadata, generate styled EPUB ebooks, and optionally send them directly to your Kindle via email.

## Features

- **Obsidian Vault Scanning**: Automatically scans a directory for folders containing Markdown (`.md`) files and recognizes them as individual notes/books.
- **Hierarchical Navigation**: Supports nested folder structures. Folders that don't contain Markdown files but have notes deeper in their hierarchy are displayed as navigable folders in the menu, letting you drill down into subcategories.
- **Metadata Management**: Generates and manages `metadata.json` for each note, including title, author(s), publisher, language, description, cover image, and more.
- **Auto Cover Detection**: If a `cover.png` or `cover.jpg` file exists in a note's directory, it is automatically used as the EPUB cover image.
- **Default Author & Publisher**: Configurable default values via environment variables so you don't need to set them for every note.
- **EPUB Generation**: Converts Markdown files to EPUB using Pandoc with:
  - Custom CSS styling optimized for e-readers (Kindle).
  - Automatic Table of Contents (up to heading level 2).
  - Line numbers in code blocks via a Lua filter.
  - Embedded images resolved from the note's directory.
- **Send to Kindle**: Optionally send the generated EPUB directly to your Kindle device via email (SMTP), with Gmail App Password support.
- **Interactive UI**: A rich terminal interface with menus, colors, emojis, and loading animations powered by [Rich](https://github.com/Textualize/rich) and [Questionary](https://github.com/tmbo/questionary).
- **Pydantic Validation**: All configuration and metadata is validated using Pydantic models.
- **Global Installation**: Install once with `uv tool install .` and run from anywhere in your system.

## Prerequisites

- Python >= 3.14
- [Pandoc](http://pandoc.org/) installed on your system.

## Setup & Configuration

1. Clone the repository and install dependencies using [uv](https://github.com/astral-sh/uv):
   ```bash
   ./install.sh
   ```
   This will install `ebook-maker` as a global CLI tool and copy your `.env` configuration to `~/.config/ebook-maker/.env`, so it works from any directory.

2. Copy the example configuration file and adjust it to your paths:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your settings:
   ```env
   # Required
   OBSIDIAN_ROOT=/path/to/your/obsidian/vault
   EPUB_DESTINATION=/path/to/save/epubs

   # Optional defaults
   DEFAULT_AUTHOR="Your Name"
   DEFAULT_PUBLISHER="Your Publisher"

   # Optional: Send to Kindle via email
   KINDLE_EMAIL="your_kindle@kindle.com"
   SMTP_USER="your_email@gmail.com"
   SMTP_PASSWORD="your_gmail_app_password"
   ```

4. Run the installer again to apply the configuration globally:
   ```bash
   ./install.sh
   ```

   > **Note:** The app looks for `.env` files in two locations (in order): `~/.config/ebook-maker/.env` (global) and `.env` in the current directory (overrides global). This means you can override settings per-project if needed.

   > **Note:** To use the Send to Kindle feature with Gmail, you need to generate an [App Password](https://support.google.com/accounts/answer/185833) and add your Gmail address to the [Approved Personal Document E-mail List](https://www.amazon.com/hz/mycd/myx#/home/settings/payment) in your Amazon account settings.

## Running the App

Once installed, you can run it from anywhere:
```bash
ebook-maker
```

Or from the project directory using the dev script:
```bash
./run.sh
```

## Running Tests

```bash
./test.sh
```

## Project Structure

```
src/ebook_maker/
├── core/           # Settings and Pydantic models
├── scanner/        # Obsidian vault scanning and metadata management
├── converter/      # EPUB generation using Pandoc
├── sender/         # Send EPUB to Kindle via email
├── ui/             # Terminal menus and display (Rich + Questionary)
├── assets/         # CSS stylesheet and Lua filter for EPUB styling
└── main.py         # Application entry point
```

## License

**"THE BEER-WARE LICENSE" (Revision 42):**
<juanpanasiti@gmail.com> wrote this file. As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return. Juan Marcelo Panasiti
