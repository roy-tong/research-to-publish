# Research beyond final deliverables

A final report is an editorial selection, not the complete evidence base. For local-project research, inspect process drafts, decision logs, audit notes, raw records and transformation scripts alongside the current deliverable.

## Read in this order

1. Index candidate files without claiming they have been read. Exclude credentials, runtime state and unrelated personal data. Filename/version labels are hints, not authority.
2. Read the current report and its version notes. Identify changed claims, omitted cases and unanswered questions.
3. Follow each change into prior drafts, review comments and decision logs. Separate new evidence, user direction, analytical correction and editorial compression. A later version is not automatically stronger evidence.
4. Trace selected claims to raw record IDs, file hashes and line numbers. Record the selection rule and actual reading scope. Decompress JSONL incrementally; sample intentionally and disclose that a keyword sample is not representative.
5. Inspect collection queries, exclusion rules, transformations and codebooks before interpreting counts. Raw, processed and balanced views may contain the same records. Do not sum them. GitHub issues endpoints may include pull requests; an issue can also contain promotion, a feature proposal or news rather than user experience.
6. Build a private lineage note: previous claim → reason for change → supporting and opposing records → current interpretation → unresolved question. Preserve superseded and rejected status rather than silently replacing history.
7. Turn useful findings into article pitches or revisions. Distinguish material useful for private reasoning from material cleared for public quotation. Do not publish an identifiable raw dataset simply because it informed the analysis.

## Required private manifest

For each selected source, record project, original relative path, SHA-256, source layer, actual coverage, record ID/line locator if applicable, predecessor/successor relationship when established, and publication scope. For derived data, record input versions and transform/codebook version where available. Unknown lineage stays unknown.

Keep index counts, scanned rows, keyword matches, manually read examples and validated conclusions separate. An automated label is not a verified observation. Never promote an assistant suggestion or a project owner's strategic preference into proof of market demand.

## Integration with the existing pipeline

This is an editorial protocol, not an automatic historical-claim resolver. Keep the manifest and selected raw excerpts in the private workspace. Import selected UTF-8 evidence extracts through `ingest`, retaining locators and the original file hash in the extract. Author claims with explicit boundaries; use casebooks for selection and the normal topic validation/review workflow before publication. When corrections affect an already imported source, re-import it and use `impact` to inspect dependent articles. Do not mark historical research as migrated until those imports and relationships exist.
