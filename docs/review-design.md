---
name: Private editorial review
description: Source-linked reading and per-entry editorial feedback
colors:
  ink: "#252525"
  muted: "#595959"
  accent: "#993d25"
  line: "#ddd8d0"
  paper: "#fbfaf7"
  control: "#ffffff"
  control-border: "#9e9990"
  control-hover: "#eee9df"
  focus: "#b95a39"
  review: "#f1ede5"
typography:
  body:
    fontFamily: 'system-ui, -apple-system, "PingFang SC", sans-serif'
    fontSize: "16px"
    lineHeight: 1.8
  reading:
    fontFamily: 'Georgia, "Songti SC", serif'
    fontSize: "18px"
    lineHeight: 1.95
rounded:
  control: "4px"
---

# Editorial review surface

## Overview

This scoped implementation record describes the HTML emitted by `research_to_publish/catalog.py`. It extends the existing simple reader with private editorial controls. The warm white page and brown links keep authored prose and evidence readable while feedback remains adjacent to each entry.

This is a source inspection, not a visual approval. No approved composition or screenshots were available; Chrome verification failed, so rendered fidelity and browser-specific behavior remain unverified. This document does not establish a replacement design system for the rest of the project.

## Colors

The accent identifies source links and disclosure controls. Ink and muted text separate primary reading from metadata; fine neutral lines divide entries. White native controls sit within a warmer review panel. Focus has its own visible outline. Colors above are extracted from the renderer, not proposed additions.

## Typography

Interface text uses the system stack; authored sections use the serif reading stack, with system headings. The page title scales from 28 to 44 px with a 1.3 line height. Entry headings are 23 px, section headings 20 px, theses 18 px, metadata 13 px, and labels 14 px. References use 14 px system text at 1.65 line height. No webfonts are loaded; actual Chinese and Latin rendering depends on installed fonts.

## Layout

Header, main, and footer share a centered 1120 px maximum width with 32 px vertical and 28 px horizontal padding. Entries form a single column separated by rules, with 26 px vertical padding. Reading sections have a centered 760 px maximum width. Expanded evidence dossiers use two equal columns with a 32 px horizontal gap.

The wrapping toolbar contains search, type, direction, status, and feedback export. At widths of 650 px or less, page padding becomes 24 by 18 px, dossier fields stack, toolbar items fill the width, reading text becomes 17 px, and entry headings become 21 px. Textareas fill the panel width and resize vertically from a 90 px minimum height.

Print CSS hides toolbar and feedback controls, removes the paper tint, and discourages entry breaks. It sets disclosures to block display but does not explicitly open closed disclosures; complete printed reading coverage is not verified.

## Elevation & Depth

The surface has no shadows or animated transitions. Borders and the review panel's tonal background provide separation.

## Shapes

Native inputs, selects, textareas, and buttons have a 1 px border, modest control radius, and 8 by 12 px padding. Entry and review regions remain rectangular. Keyboard focus uses a 3 px outline with a 3 px offset on controls, disclosures, and links.

## Components

- Each entry presents a title, type/direction/stage metadata, thesis, expandable authored sections and evidence, source links, related-entry links, and a feedback panel. Article entries require at least three authored sections; rendering does not write or fact-check them.
- Native disclosures keep the initial view compact. Related-entry anchors clear filters and open the destination disclosure. External evidence links open a separate tab with `noopener noreferrer`.
- Feedback offers pending, keep, revise, and defer states plus a free-text comment. Labels associate with controls. Counts and save/export messages use status regions. Export focuses the comment field and reports an error if revise or defer lacks a reason.
- Search and filters hide unmatched entries and show an empty state. Changing an entry decision saves feedback but does not immediately rerun the active status filter; the next filter input refreshes visibility.
- Per-entry decisions and comments persist in browser `localStorage`, namespaced by the catalog hash. A changed catalog uses a separate namespace. Storage is browser/origin dependent, can be unavailable or cleared, and is not an access-control mechanism or synchronized database. The renderer reports storage failures; JSON export is the transfer path, with no automatic upload or browser-side import.
- Export includes every entry, defaults untouched entries to pending, and binds feedback to the catalog revision. Pipeline import validates that revision. Neither keep, export, nor import approves publication.

## Do's and Don'ts

- Preserve the simple reading surface, native controls, visible focus, and linked evidence when extending this page.
- Keep source statements distinct from authored interpretation and editorial feedback.
- Keep actual research and generated private review pages outside the public code repository.
- Do not treat structural validation as editorial quality review or verification of source claims.
- Do not describe browser rendering, persistence across environments, or print completeness as verified without testing them.
- Do not turn a keep decision into publication approval.
