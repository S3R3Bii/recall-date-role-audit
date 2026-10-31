# Fixed event-role audit

## Decision and source-informed scope

Can a generic owner-notification field be attached to a final-notification or remedy-availability event without checking the dated documents? Audit a finite source cohort and build a local guard that preserves event type and date certainty.

The original Study 18 plan to predict time to final remedy from initial Part 573 information remains unexecuted. Its label and initial-vintage gates remain unresolved. This separate execution is a descriptive measurement/lineage audit and typed-event implementation exercise. It does not fit a survival model, validate a physical remedy-availability date, measure delivered repairs or establish safety/financial benefits.

Source discovery inspected the official 29-field recall dictionary, the documented 2012 BMW API example and its 13 associated document labels, and public documentation distinguishing interim and remedy notices. A search also exposed one 2023 Volvo notification date before this plan. Selection is therefore source informed, not blinded. The finite cohort below is fixed by campaign number, not observed timing.

## Fixed cohort and source capture

Query every campaign ID 23V001000 through 23V012000, inclusive. Preserve every query, including a valid no-record response, without replacing campaigns. Use the documented campaign-number API and the official post-2010 recall flat file, plus every available Part 573 report, recall acknowledgement, interim owner notice, remedy/final owner notice and general owner-notification letter exposed in each campaign's official associated-document list. Dealer bulletins, repeated quarterly performance tables and vehicle-specific VIN lookups are outside scope. Do not infer the date or type of a missing document.

Capture the native flat-file schema before projection. Preserve all distinct report-received and owner-notification dates for every matching native row, including missing/sentinel values, with source-row counts. Do not resolve conflicting campaign-level dates by selecting a convenient row. API records can repeat across vehicle models; retain all native response records privately and reconcile distinct date/prose assertions before any campaign aggregation. Company contact information, VINs, worker/owner identifiers and full source ZIPs/PDFs stay private.

Document metadata and exact URLs are collected from the official list before content review. Native source hashes, retrieval times, campaign IDs and document IDs are retained. A filename's year or upload date is not an event date. Reports may be amended; the earliest captured report is not automatically an original filing. No reconstructed historical feature availability is claimed.

## Prespecified coding and comparison

For every source document, retain its type, an explicit printed event/letter date when present, whether the date is planned or asserted as past, whether the text explicitly calls the notice interim, whether it explicitly says a remedy is available or not yet available, and a page reference plus a short evidence clause. If these are unclear or conflict, mark unknown. Draft or sample owner letters alone do not prove mailing. A reported mailing date in an acknowledgement or current source is an attributed assertion, not independently verified delivery.

For each of the twelve campaigns, compare each distinct usable ODATE value against the audited document evidence. Classify MATCH_INTERIM only when dated interim-notification evidence explicitly binds that same date; MATCH_REMEDY_NOTICE only when a documented remedy/final owner-notification event explicitly binds that date; MATCH_GENERIC_NOTICE when only a generic owner-notice event is supported; CONFLICTING_DATES when incompatible source assertions prevent a unique binding; or UNRESOLVED when no supported mapping exists. Date coincidence alone does not imply event identity. A field may match a notice date while physical first remedy availability remains unknown. Never call a generic or remedy-notice date a verified physical availability date.

Retain the case table and all evidence records, not only discrepancies. Report the twelve request outcomes, number of campaigns with usable field dates, event-role categories, missing/ambiguous evidence, and any signed day differences between explicitly supported dates. List every denominator. If there are no comparable dated events, report unavailable rather than zero delay. Multiple notices within a campaign are related, and twelve early numbered campaigns cannot estimate a national error rate or remedy-time distribution.

## Implementation and independent verification

The local exercise accepts a typed event with campaign ID, event role, date, planned/reported state, evidence ID and evidence status. It must reject missing evidence, planned dates presented as actual, ambiguous dates, unsupported role conversions and any attempt to relabel a notification as physical remedy availability. An explicitly supported notice can retain its notice role. It must never fill an unknown availability date from ODATE. No learned classifier, tuned threshold, seed, calibration, statistical test or ranking is used.

Before comparisons, commit the source projection, all source exclusions and document adjudication table. Freeze source/method dependencies before the first summary command. Native dates and identifiers are exact; independent SQLite joins and calendar arithmetic reconstruct every category/count/day difference without production helpers. Independently check raw flat/API projection against retained originals and document-date/page clauses against extracted text and rendered source pages. Do not resolve substantive ambiguity by a second model's opinion; retain unknown. Authored fixtures cover planned-vs-reported events, leap days, date conflicts, unsupported role conversion, missing evidence and empty denominators.

## Acceptance, publication and stop rule

Required gates: exact licensed factual source projection and complete fixed case accounting; documented event-role evidence with unknowns preserved; independent source/count/calendar/guard checks; two isolated saved-data Python replays; scoped privacy; source-bound figures; a concise rendered independent manuscript; exact candidate/main Linux CI, matching tree, annotated tag and synchronized metadata. All applicable gates must pass before counting a scoped release. The broader remedy-time prediction remains unexecuted even if this audit completes.

Grade 4 means those finite criteria pass. It does not establish general label validity, historical first delivery, causal effects, calibrated prediction, actual repair availability or safety impact. Keep at most three substantive review rounds, 45 active review minutes and 60 review-specific calls across source context and execution. Preserve failures; stop a persistent defect after one targeted retry. Source records unavailable or document evidence insufficient for required provenance leave the study incomplete rather than prompting an outcome-based cohort replacement.
