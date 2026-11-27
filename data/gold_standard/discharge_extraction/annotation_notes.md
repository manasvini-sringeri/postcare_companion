# Gold-standard extraction examples

Eight fully fictional, hand-authored examples for extraction testing. They are not patient records, prescriptions or clinical advice.

## Files
- `gold_summaries.jsonl`: source text, one record per line.
- `expected_extractions.jsonl`: manually authored expected structured extraction.
- Each populated extracted item includes `source_text_span` for traceability.

## Annotation rules
1. Extract only what the source text explicitly states.
2. Missing information stays null or an empty list; do not infer.
3. A medication duration or PRN maximum frequency not stated in the note remains null.
4. Relative dates are resolved only where an explicit interval and discharge date make the calculation unambiguous.
5. Rehab/activity items are copied from the summary; no exercise prescription is added.
6. `Med-A` through `Med-H` are placeholders, not real medicines.
7. Urgency labels reproduce the fictional note's own instruction and are not independently clinically validated.

## Coverage
GOLD-001: medication, follow-up interval, relative test date, activity and red flags.
GOLD-002: COPD-labelled case, inhaled route and explicit breathing-technique schedule.
GOLD-003: procedure, dated wound review, restrictions and wound warnings.
GOLD-004: pending test result and relative follow-up.
GOLD-005: missing medicine duration and relative test date.
GOLD-006: explicit follow-up date and incomplete restriction detail.
GOLD-007: TIA warnings; no rehab instruction inferred.
GOLD-008: PRN medication with missing maximum frequency and conditional follow-up.

Have a second reviewer independently verify all labels before using this set for reported extraction metrics. Keep this set out of model training and use it for evaluation/testing.
