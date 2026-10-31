# Event coding rules

This is a source-informed audit of twelve fixed campaigns, not a model for time to remedy. Raw dates were visible during source review. The adjudication table is committed before comparison code runs; this order is not blindness.

- **Document date** means the printed date of the particular letter or filing. A SAMPLE watermark, placeholders, month-only date, or an issued-list label does not establish mailing or delivery.
- **Planned notice** is an expected date or structured planned range. Later amendments and old narrative plans stay separate. A past calendar day inside a planned field does not become a reported event.
- **Reported generic notice** requires explicit past notification language in the current official API or filing. It remains an attributed source assertion, with no independent delivery verification.
- **Interim binding** requires an exact reported event date explicitly attached to the interim notice. An undated interim template is insufficient.
- **Remedy/final notice binding** requires an exact reported event date explicitly attached to a campaign-specific remedy/final notice. Repair instructions alone, a generic final-letter template, or a month-only SAMPLE assertion is insufficient. These conservative rules may leave a real event unresolved.
- **Physical first availability** requires separate first-availability evidence. It is unknown throughout this audit, including when a letter describes an available repair. Channel-dependent dealer and OTA statements remain distinct.

The comparison accepts every distinct flat-file ODATE token. Invalid/missing tokens stay unresolved; multiple usable dates are conflicting. For a unique field date, compare all distinct **reported** notification assertions. Different reported dates yield CONFLICTING_DATES; equal dates with explicit role binding yield MATCH_INTERIM, MATCH_REMEDY_NOTICE or MATCH_GENERIC_NOTICE. With no reported assertion there is UNRESOLVED. Planned API dates and printed letter dates can be displayed alongside the field but cannot by themselves create a reported binding.

A conflict is a source discrepancy requiring investigation. Unspecified phases or revisions might explain it; this audit does not establish that an agency date is erroneous. Different brand letters do not automatically conflict.

Signed differences are flat ODATE minus explicitly reported generic notification date, in calendar days. A zero means date equality between those source fields, not zero repair delay. No comparable reported event means unavailable. Planned range endpoints are retained in a separate descriptive table; they are never treated as actual lateness.

The case table retains all twelve campaigns, seven API past assertions and five planned assertions regardless of match. The selection was fixed by campaign number, not by discrepancies. There is no national sampling claim, causal effect, safety validation, cost saving, learned threshold or new estimator. The guard is an authored defensive software exercise, not a deployed recall-management system.
