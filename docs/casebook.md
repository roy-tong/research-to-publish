# Casebooks before publication

The casebook is a private editorial inbox upstream of topics. It keeps broad discovery, a specific angle, authored articles and channel plans reviewable without treating every discovered project as a finished article.

```sh
r2p --workspace PRIVATE catalog-check --file PRIVATE/catalog.json
r2p --workspace PRIVATE catalog-build --file PRIVATE/catalog.json --to PRIVATE/review-v1.html
r2p --workspace PRIVATE catalog-feedback --file PRIVATE/catalog.json --feedback DOWNLOADED.json --to PRIVATE/reviews/round-1.json
```

Schema version 1 has `title`, `intro`, `sources`, `entries`. Each source has `id`, `label`, HTTPS `url` without credentials/query/fragment, `note` and `checked_at`. Record what was actually inspected; a homepage is evidence of the vendor's positioning, not independent proof of performance, customers or revenue.

Start from [the synthetic example](../examples/casebook.json); copy it into your private workspace before adding real research. The renderer is documented in [review surface design](review-design.md).

Each entry has `id`, `kind` (`case`, `pitch`, `article`, `strategy`), `title`, `group`, `stage`, `question`, `thesis`, `detail`, `evidence`, `edge`, `connection`, `next_step`, and `source_ids`. Optional `related` contains other entry IDs. Authored `sections` contain `heading`, `text` (blank-line separated paragraphs) and `source_ids` belonging to that entry. Articles require at least three sections. These are structural requirements, not quality scores.

Review HTML supports text/type/direction/status filters, section links, per-entry choices and notes, and feedback JSON download. Notes stay in browser storage, scoped to the complete catalog fingerprint. Storage failure is visible. Export before switching browsers or revising the catalog; this is not server-side sync. `revise` and `drop` require an explanation. Import rejects stale revisions, unknown/duplicate IDs and unknown choices, and never overwrites an existing receipt.

**Keep means retain for editorial work, never publish.** Imported feedback does not call topic review, export, or publish. After selection, author the topic and claims, resolve research gaps, build and run the existing publication review. The schema does not independently validate source claims or invent prose. No automatic quality score is provided.

## Editorial commissioning

Find cases through a mechanism, not a company-name quota: a surprising bundle, a payer different from the user, an unexpected distribution route, a product boundary, a durable asset, an exit or failed assumption. Keep a nearby counterexample. Distinguish vendor documentation, customer-reported deployment, measured results and author interpretation.

An article needs a reader question, a concrete object, a causal explanation, the strongest alternative and a change in the reader's decision. A research inventory is an input. An article should not narrate the inventory or replace its own argument with repeated disclaimers. Cite factual details next to the relevant section; let the reasoning carry the story.

Casebook data is private. Do not place real projects, personal research, account identifiers, unpublished strategy or browser feedback inside this public code repository.
