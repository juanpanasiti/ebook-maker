## Why

The current note action menu presents conversion and navigation actions in an order that makes the primary output flow less obvious. Reordering the actions will put the most common generation paths first and reduce friction when working through a selected note.

## What Changes

- Reorder the selected-note action menu so it presents the primary actions first: Generate EPUB, Generate PDF, Send EPUB to Kindle, Open EPUB/PDF Location, View Metadata, Edit Metadata, Back to Note Selection.
- Replace the separate EPUB and PDF location entries with a single shared output-location action, since both formats are written to the same destination directory.
- Preserve conditional visibility for actions that depend on runtime state, such as Kindle sending and output-location access.
- Keep the underlying generation, metadata, and sending behavior unchanged.

## Capabilities

### New Capabilities
- `note-action-menu`: Defines the ordering and availability of the actions shown after selecting a note, including the shared output-location entry.

### Modified Capabilities

## Impact

The change is confined to the CLI interaction layer in `src/ebook_maker/ui/` and the action dispatch loop in `src/ebook_maker/main.py`. It does not require changes to the domain models in `core/`, the scanner, converter logic, sender logic, or application settings. Tests will need to cover the updated menu order and the merged output-location behavior.
