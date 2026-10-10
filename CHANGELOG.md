# Changelog

## Unreleased

- Add private casebooks for broad case discovery, article drafts, pitches and channel plans.
- Render standalone HTML with filters, per-entry review notes and downloadable feedback.
- Bind imported feedback to the complete catalog revision; reject stale reviews and refuse receipt overwrites. Editorial selection never grants publication approval.
- Validate source references and article sections; escape supplied text and restrict public source URLs. These checks do not establish factual accuracy or article quality.
- Add six tests; the full suite now contains 34 tests.

## 0.2.1

- Optional `--label` on `ingest` (or a `label` field in sync configs): a reader-facing name used for public reference links in built articles instead of the internal source ID.
- Renderer version 4: adding or changing a label invalidates earlier reviews via the fingerprint, as before.

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
