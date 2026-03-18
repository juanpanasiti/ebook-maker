import sys

from ebook_maker.core.settings import get_settings
from ebook_maker.core.models import Folder
from ebook_maker.scanner.scanner import scan_vault, scan_directory
from ebook_maker.ui.console import console
from ebook_maker.ui.menu import (
    display_no_notes_found, 
    display_welcome_banner, 
    prompt_select_note,
    prompt_note_action,
    display_note_metadata,
    prompt_edit_metadata
)
from ebook_maker.converter.converter import generate_epub, get_epub_output_filename
from ebook_maker.converter.pdf_converter import generate_pdf, get_pdf_output_filename
from ebook_maker.sender.email_sender import send_epub_to_kindle


def main():
    display_welcome_banner()

    try:
        settings = get_settings()
    except Exception as e:
        console.print("[bold red]Configuration Error:[/bold red]")
        console.print(f"Please ensure you have a valid .env file at ~/.config/ebook-maker/.env or in the current directory. Details:\n{e}")
        sys.exit(1)

    with console.status("[bold cyan]Scanning Obsidian vault for notes...[/bold cyan]", spinner="dots"):
        notes = scan_vault(
            settings.obsidian_root, 
            default_author=settings.default_author,
            default_publisher=settings.default_publisher
        )

    if not notes:
        display_no_notes_found()

    # Inform user how many were found
    console.print(f"✅ Found [bold green]{len(notes)}[/bold green] note(s).\n")

    # Navigation stack for hierarchical folder browsing
    nav_stack: list = [settings.obsidian_root]

    while True:
        console.clear()
        display_welcome_banner()
        console.print(f"✅ Found [bold green]{len(notes)}[/bold green] note(s).\n")

        current_dir = nav_stack[-1]
        if current_dir != settings.obsidian_root:
            console.print(f"[bold cyan]📂 {current_dir.name}[/bold cyan]\n")

        entries = scan_directory(
            current_dir,
            default_author=settings.default_author,
            default_publisher=settings.default_publisher
        )

        if not entries:
            if len(nav_stack) == 1:
                display_no_notes_found()
            else:
                console.print("[dim]No notes found in this folder. Going back...[/dim]")
                nav_stack.pop()
                continue

        selected = prompt_select_note(entries, show_back=len(nav_stack) > 1)

        if not selected or selected == "exit":
            console.clear()
            sys.exit(0)

        if selected == "back":
            nav_stack.pop()
            continue

        if isinstance(selected, Folder):
            nav_stack.append(selected.path)
            continue

        selected_note = selected

        while True:
            action = prompt_note_action(selected_note, settings)
            
            if not action or action == "back":
                break
            
            if action == "view":
                display_note_metadata(selected_note)
            
            elif action == "edit":
                prompt_edit_metadata(selected_note)
            
            elif action == "open_location":
                import subprocess
                epub_path = settings.epub_destination / get_epub_output_filename(selected_note)
                subprocess.Popen(["xdg-open", str(epub_path.parent)])
                console.print(f"📂 [bold green]Opened:[/bold green] {epub_path.parent}\n")

            elif action == "open_pdf_location":
                import subprocess
                pdf_path = settings.epub_destination / get_pdf_output_filename(selected_note)
                subprocess.Popen(["xdg-open", str(pdf_path.parent)])
                console.print(f"📂 [bold green]Opened:[/bold green] {pdf_path.parent}\n")

            elif action == "generate_pdf":
                try:
                    console.print(f"\n[bold green]Generating PDF for:[/bold green] {selected_note.metadata.title}")

                    with console.status(
                        "[bold cyan]Converting Markdown → HTML → PDF (WeasyPrint)...[/bold cyan]",
                        spinner="bouncingBar"
                    ):
                        output_path = generate_pdf(selected_note, settings.epub_destination)

                    console.print(f"🎉 [bold green]Success![/bold green] PDF generated at: [blue]{output_path}[/blue]\n")

                except Exception as e:
                    console.print(f"❌ [bold red]Failed action:[/bold red] {e}")

            elif action == "generate":
                try:
                    console.print(f"\n[bold green]Generating EPUB for:[/bold green] {selected_note.metadata.title}")
                    
                    with console.status(
                        "[bold cyan]Converting Markdown files using Pandoc...[/bold cyan]", 
                        spinner="bouncingBar"
                    ):
                        output_path = generate_epub(selected_note, settings.epub_destination)
                    
                    console.print(f"🎉 [bold green]Success![/bold green] EPUB generated at: [blue]{output_path}[/blue]\n")
                    
                    # Ask if they want to send to Kindle (only if configured)
                    if settings.kindle_email and settings.smtp_user and settings.smtp_password:
                        import questionary
                        send = questionary.confirm(
                            f"Send to Kindle? ({settings.kindle_email})",
                            default=True
                        ).ask()
                        if send:
                            with console.status("[bold cyan]Sending EPUB to Kindle via SMTP...[/bold cyan]", spinner="dots"):
                                send_epub_to_kindle(output_path, settings)
                            console.print("📧 [bold green]Sent Successfully![/bold green] Check your Kindle in a few minutes.\n")
                        
                except Exception as e:
                    console.print(f"❌ [bold red]Failed action:[/bold red] {e}")
                    
            elif action == "send":
                try:
                    # Construct expected output path
                    output_filename = get_epub_output_filename(selected_note)
                    output_path = settings.epub_destination / output_filename
                    
                    if not output_path.exists():
                        console.print(f"\n[bold yellow]EPUB not found. Generating first...[/bold yellow]")
                        with console.status(
                            "[bold cyan]Converting Markdown files using Pandoc...[/bold cyan]", 
                            spinner="bouncingBar"
                        ):
                            output_path = generate_epub(selected_note, settings.epub_destination)
                        console.print(f"🎉 [bold green]Generated![/bold green] EPUB saved at: [blue]{output_path}[/blue]")
                    
                    console.print(f"\n[bold green]Sending EPUB to:[/bold green] {settings.kindle_email}")
                    with console.status(f"[bold cyan]Sending {output_filename} to Kindle via SMTP...[/bold cyan]", spinner="dots"):
                        send_epub_to_kindle(output_path, settings)
                    console.print("📧 [bold green]Sent Successfully![/bold green] Check your Kindle in a few minutes.\n")
                    
                except Exception as e:
                    console.print(f"❌ [bold red]Failed action:[/bold red] {e}")


if __name__ == "__main__":
    main()
