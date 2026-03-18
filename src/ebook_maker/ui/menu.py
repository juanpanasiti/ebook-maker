import sys
from typing import Optional

import questionary

from ebook_maker.core.models import Folder, Note, NoteMetadata, VaultEntry
from ebook_maker.converter.converter import get_epub_output_filename
from ebook_maker.converter.pdf_converter import get_pdf_output_filename
from ebook_maker.core.settings import Settings
from ebook_maker.scanner.scanner import write_metadata
from ebook_maker.ui.console import console
from rich.table import Table
from rich.panel import Panel


def display_welcome_banner():
    """Shows the application welcome message and banner."""
    console.print()
    console.print("[bold cyan]╔════════════════════════════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║[/bold cyan]             [bold yellow]📚 Obsidian to EPUB & PDF Maker[/bold yellow]                   [bold cyan]║[/bold cyan]")
    console.print("[bold cyan]╚════════════════════════════════════════════════════════════════╝[/bold cyan]")
    console.print()


def display_no_notes_found():
    """Displays a message when no notes are found in the root directory."""
    console.print("[bold red]❌ No notes found in the configured Obsidian Root.[/bold red]")
    console.print("[dim]A note is considered valid if it's a folder containing at least one .md file.[/dim]")
    sys.exit(0)


def prompt_select_note(entries: list[VaultEntry], show_back: bool = False) -> Optional[Note | Folder | str]:
    """
    Displays an interactive menu for the user to select a note or navigate into a folder.
    Returns the selected Note/Folder object, "back", "exit", or None if the user cancels.
    """
    choices = []
    for entry in entries:
        if isinstance(entry, Note):
            choices.append(questionary.Choice(
                title=[
                    ("class:text", "📘 "),
                    ("class:title", f"{entry.metadata.title} "),
                    ("class:dim", f"({len(entry.markdown_files)} files)"),
                ],
                value=entry,
            ))
        else:
            choices.append(questionary.Choice(
                title=[
                    ("class:text", "📁 "),
                    ("class:folder", entry.name),
                ],
                value=entry,
            ))

    if show_back:
        choices.append(questionary.Choice(title="🔙 Back", value="back"))
    choices.append(questionary.Choice(title="❌ Exit", value="exit"))

    # We use a custom style for questionary
    custom_style = questionary.Style(
        [
            ("qmark", "fg:#673ab7 bold"),        # question mark
            ("question", "fg:#101010 bold"),      # question text
            ("answer", "fg:#f44336 bold"),       # submitted answer text behind the question
            ("pointer", "fg:#00bcd4 bold"),      # pointer used in select and checkbox prompts
            ("highlighted", "fg:#00bcd4 bold"),  # pointed-at choice in select and checkbox prompts
            ("selected", "fg:#cc5454"),          # style for a selected item of a checkbox
            ("separator", "fg:#cc5454"),         # separator in lists
            ("instruction", "fg:#808080"),       # user instructions for select, rawselect, checkbox
            ("text", "fg:#ffffff"),              # plain text
            ("title", "fg:#00ff00 bold"),        # custom style we used in note title
            ("folder", "fg:#f0c040 bold"),       # custom style for folder names
            ("dim", "fg:#808080"),               # custom style we used in note files count
        ]
    )

    console.print("[bold green]Select a note to convert to EPUB:[/bold green]")
    selected_note = questionary.select(
        "",  # Empty message because we print our own header using rich above
        choices=choices,
        style=custom_style,
        use_indicator=True,
    ).ask()

    return selected_note


def prompt_note_action(note: Note, settings: Settings) -> Optional[str]:
    """Asks the user what to do with the selected note."""
    choices = [
        questionary.Choice("🔍 View Metadata", "view"),
        questionary.Choice("✏️  Edit Metadata", "edit"),
        questionary.Choice("🚀 Generate EPUB", "generate"),
        questionary.Choice("📄 Generate PDF (A4)", "generate_pdf"),
    ]

    # Only show 'Open EPUB location' if the EPUB file exists
    epub_path = settings.epub_destination / get_epub_output_filename(note)
    if epub_path.exists():
        choices.append(questionary.Choice("📂 Open EPUB Location", "open_location"))

    # Only show 'Open PDF location' if the PDF file exists
    pdf_path = settings.epub_destination / get_pdf_output_filename(note)
    if pdf_path.exists():
        choices.append(questionary.Choice("📂 Open PDF Location", "open_pdf_location"))

    # Only show the option to send to Kindle if the configuration is active
    if settings.kindle_email and settings.smtp_user and settings.smtp_password:
        choices.append(questionary.Choice("📧 Send EPUB to Kindle", "send"))

    choices.append(questionary.Choice("🔙 Back to Note Selection", "back"))

    console.print(f"\n[bold green]What would you like to do with:[/bold green] {note.metadata.title}?")
    action = questionary.select(
        "",
        choices=choices,
        use_indicator=True,
    ).ask()

    return action


def display_note_metadata(note: Note) -> None:
    """Displays the note's metadata in a nicely formatted Rich Table."""
    table = Table(title=f"Metadata for '{note.metadata.title}'", show_header=False, box=None)
    table.add_column("Property", style="bold cyan", justify="right")
    table.add_column("Value", style="white")

    table.add_row("Title", note.metadata.title)
    table.add_row("Author", note.metadata.author)
    table.add_row("Publisher", note.metadata.publisher if note.metadata.publisher else "[dim]None[/dim]")
    table.add_row("Language", note.metadata.language)
    table.add_row("Date", note.metadata.date if note.metadata.date else "[dim]None[/dim]")
    table.add_row("Identifier (UUID/ISBN)", note.metadata.identifier if note.metadata.identifier else "[dim]None[/dim]")
    table.add_row("Description", note.metadata.description if note.metadata.description else "[dim]None[/dim]")
    table.add_row("Cover Image", note.metadata.cover_image if note.metadata.cover_image else "[dim]None[/dim]")
    table.add_row("Finished", "Yes" if note.metadata.finished else "No")
    table.add_row("Markdown Files", str(len(note.markdown_files)))

    console.print()
    console.print(Panel(table, border_style="cyan", expand=False))
    console.print()


def prompt_edit_metadata(note: Note) -> None:
    """Prompts the user to edit specific metadata properties via a menu."""
    while True:
        choices = [
            questionary.Choice(f"Title: {note.metadata.title}", "title"),
            questionary.Choice(f"Author: {note.metadata.author}", "author"),
            questionary.Choice(f"Publisher: {note.metadata.publisher or 'None'}", "publisher"),
            questionary.Choice(f"Language: {note.metadata.language}", "language"),
            questionary.Choice(f"Description: {note.metadata.description or 'None'}", "description"),
            questionary.Choice(f"Identifier: {note.metadata.identifier or 'None'}", "identifier"),
            questionary.Choice(f"Cover Image: {note.metadata.cover_image or 'None'}", "cover_image"),
            questionary.Choice(f"Finished: {'Yes' if note.metadata.finished else 'No'}", "finished"),
            questionary.Choice("🔙 Back", "back"),
        ]

        console.print(f"\n[bold yellow]Editing metadata for:[/bold yellow] {note.metadata.title}")
        choice = questionary.select(
            "Select property to edit:",
            choices=choices,
            use_indicator=True,
        ).ask()

        if not choice or choice == "back":
            break

        if choice == "title":
            new_val = questionary.text("Title:", default=note.metadata.title).ask()
            if new_val is not None:
                note.metadata.title = new_val
        elif choice == "author":
            new_val = questionary.text("Author:", default=note.metadata.author).ask()
            if new_val is not None:
                note.metadata.author = new_val
        elif choice == "publisher":
            current_pub = note.metadata.publisher or ""
            new_val = questionary.text("Publisher:", default=current_pub).ask()
            if new_val is not None:
                note.metadata.publisher = new_val if new_val.strip() else None
        elif choice == "language":
            new_val = questionary.text("Language:", default=note.metadata.language).ask()
            if new_val is not None:
                note.metadata.language = new_val
        elif choice == "description":
            current_desc = note.metadata.description or ""
            new_val = questionary.text("Description:", default=current_desc).ask()
            if new_val is not None:
                note.metadata.description = new_val if new_val.strip() else None
        elif choice == "identifier":
            current_id = note.metadata.identifier or ""
            new_val = questionary.text("Identifier (UUID/ISBN):", default=current_id).ask()
            if new_val is not None:
                note.metadata.identifier = new_val if new_val.strip() else None
        elif choice == "cover_image":
            current_cover = note.metadata.cover_image or ""
            new_val = questionary.text("Cover Image Path (optional):", default=current_cover).ask()
            if new_val is not None:
                note.metadata.cover_image = new_val if new_val.strip() else None
        elif choice == "finished":
            new_val = questionary.confirm("Is this note finished?", default=note.metadata.finished).ask()
            if new_val is not None:
                note.metadata.finished = new_val

        # Save to disk after every change
        metadata_path = note.path / "metadata.json"
        write_metadata(metadata_path, note.metadata)
        console.print("[bold green]✅ Property updated![/bold green]")
