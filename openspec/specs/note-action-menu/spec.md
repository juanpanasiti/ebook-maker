## ADDED Requirements

### Requirement: Ordered note action menu
The system MUST present the selected-note action menu in this order: Generate EPUB, Generate PDF, Send EPUB to Kindle, Open EPUB/PDF Location, View Metadata, Edit Metadata, Back to Note Selection.

#### Scenario: Menu shows the requested order
- **WHEN** a user selects a note and the action menu is displayed
- **THEN** the actions appear in the specified order

#### Scenario: Back remains last
- **WHEN** the action menu is displayed
- **THEN** Back to Note Selection appears after all other actions

### Requirement: Shared output location action
The system MUST expose a single Open EPUB/PDF Location action that opens the common destination directory used for both EPUB and PDF outputs.

#### Scenario: Output directory is shared
- **WHEN** either an EPUB or a PDF has been generated for the selected note
- **THEN** the shared output-location action opens the destination directory that contains both files

#### Scenario: No output location when nothing exists
- **WHEN** neither generated output exists for the selected note
- **THEN** the shared output-location action is not shown

### Requirement: Kindle action remains conditional
The system MUST only show Send EPUB to Kindle when the Kindle email configuration is complete.

#### Scenario: Kindle sending is available
- **WHEN** kindle_email, smtp_user, and smtp_password are configured
- **THEN** the menu includes Send EPUB to Kindle in the action list

#### Scenario: Kindle sending is unavailable
- **WHEN** any Kindle sending credential is missing
- **THEN** the menu omits Send EPUB to Kindle