# Recovery check-in data dictionary

| Column | Meaning |
|---|---|
| patient_id | Anonymous synthetic identifier |
| diagnosis_group | Fictional scenario label |
| day_number | Day 1–14 |
| checkin_date | Simulated ISO date |
| pain_score_0_10 | Simulated self-reported pain score |
| temperature_c | Simulated temperature; blank if not measured |
| feeling_feverish | Simulated yes/no response |
| symptoms_reported | Semicolon-separated symptom checklist |
| medicines_taken_today | Simulated adherence response |
| rehabilitation_or_activity_done | Simulated activity/adherence response |
| free_text_note | Optional fictional comment |
| data_type | Always `synthetic_simulation` |
| clinical_status | Always `not_assessed` |

The file is for software demonstration and testing, not clinical decision-making.
