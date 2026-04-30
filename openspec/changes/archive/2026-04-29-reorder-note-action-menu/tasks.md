## 1. UI menu changes

- [x] 1.1 Update `src/ebook_maker/ui/menu.py` to reorder the selected-note actions so generation and sending actions appear before metadata actions, and replace the separate EPUB/PDF location entries with a single shared `open_location` choice.

## 2. Action dispatch changes

- [x] 2.1 Update `src/ebook_maker/main.py` to handle the merged shared-location action against the common destination directory and remove the obsolete PDF-specific open-location branch.

## 3. Regression tests

- [x] 3.1 Update `tests/ui/test_menu_actions.py` to assert the new action order and the conditional visibility of Kindle and shared output-location actions.
- [x] 3.2 Add or update a dispatcher regression test in `tests/test_main.py` to verify the shared output-location action opens the correct directory and still leaves generation and metadata actions unchanged.
