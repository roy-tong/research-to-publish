# Changelog

## 0.2.0

- Select one or more publication channels per topic; keep unselected drafts private. Existing topics default to all three channels.
- Record routing decisions and invalidate earlier approval when routing changes.
- Import private questions, expression feedback and counterevidence with idempotent IDs; retain explicit resolution notes.
- Block review/export on unresolved counterevidence and require another review after resolution.
- Query source reuse, affected sections and publication receipts across topics with `impact`.
- Include open feedback in writing briefs; distinguish published versions needing a recheck from versions needing revision.
- Correct release metadata: exporting a package without staging a site no longer reports site staging.
- Add editorial decision guide, feedback commands and upgrade instructions. Renderer version 3 invalidates old reviews without migrating workspace data.

Validation: 27 unit/integration tests. Platform analytics, live browser capture, global claim identity and autonomous publishing remain outside this release.
