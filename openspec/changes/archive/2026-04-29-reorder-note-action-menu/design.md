## Context

The selected-note action menu is built in `src/ebook_maker/ui/menu.py` and consumed in the interactive loop in `src/ebook_maker/main.py`. Today the menu exposes separate EPUB and PDF location entries even though both formats are written to the same destination directory, and the ordering places metadata actions before generation actions.

This change is limited to the CLI UI layer and the dispatch logic that interprets the selected action. It does not alter note scanning, metadata models, conversion pipelines, or SMTP delivery behavior.

## Goals / Non-Goals

**Goals:**
- Reorder the selected-note action menu to prioritize generation and delivery actions.
- Collapse the separate EPUB and PDF location entries into a single shared output-location action.
- Preserve the existing conditional visibility rules for Kindle sending and for output-location access.
- Keep the implementation within the existing `ui/` and `main.py` layers.

**Non-Goals:**
- Changing how EPUB or PDF files are generated.
- Changing where EPUB or PDF files are written.
- Modifying metadata editing behavior or the metadata model.
- Adding new configuration values or environment variables.
- Changing the folder-navigation menu or note-selection flow.

## Decisions

1. Keep the action ordering logic in `ui/menu.py`.
The menu presentation belongs to the UI layer, so the ordering should be decided where the choices are assembled rather than in the dispatcher. This keeps rendering concerns separate from behavior execution and avoids spreading ordering rules into `main.py`.

2. Map both output formats to a single location action.
Both EPUB and PDF are already written to the same output directory, so showing two separate open-location entries duplicates state without providing different behavior. A single shared action is clearer and reduces menu noise.

3. Keep dispatch handling in `main.py` compatible with the existing action loop.
The interactive loop should continue to branch on simple action values from the menu. The dispatcher can open the shared destination directory without changing conversion or sender code paths.

4. Preserve conditional menu items instead of always showing them.
Kindle sending should remain hidden until the SMTP and Kindle settings are complete, because exposing an unavailable action would degrade the CLI experience.

## Risks / Trade-offs

- [Low] Users who were accustomed to the previous ordering may need one interaction to adapt -> Mitigation: the new order follows the primary workflow more closely and is documented in the spec.
- [Low] A shared location action could be mistaken for per-format output paths -> Mitigation: label it explicitly as Open EPUB/PDF Location and keep the target directory unchanged.
- [Low] Menu tests may become brittle if they assert raw choice indices -> Mitigation: update tests to assert semantic ordering and visible labels instead of incidental implementation details.

## Migration Plan

This change can be deployed directly with no data migration. The only runtime effect is the order and labeling of one interactive menu. If needed, rollback is limited to restoring the previous menu construction and dispatch branches.

## Open Questions

None.
