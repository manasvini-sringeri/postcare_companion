# 🏥 PostCare Companion
### AI-Assisted Post-Hospitalisation Recovery and Monitoring

**BioForge 2026 | Track 1: AI-Assisted Healthcare Management | Problem Statement 4**

## 1. Overview

PostCare Companion is an AI-assisted healthcare platform designed to support patients during their recovery after hospital discharge.
It converts discharge summaries into personalised recovery plans, helps patients follow medication schedules, tracks daily health updates, and identifies potential health risks. It also provides healthcare professionals with a dashboard to monitor patient recovery and receive alerts.

## 2. Problem Statement

Patients often face difficulties after hospital discharge, including:
- Understanding medical instructions in discharge summaries.
- Remembering medication schedules and follow-up appointments.
- Tracking recovery progress and prescribed exercises.
- Identifying early warning signs of complications.

These challenges can lead to poor recovery management and potentially avoidable hospital readmissions.

## 3. Key Features

- **Discharge Summary Extraction:** Extracts medications, follow-ups, pending tests, exercises, restrictions, and warning signs.
- **Personalised Recovery Plan:** Converts extracted information into a structured, dated recovery schedule.
- **Smart Reminders:** Tracks completed and missed tasks, with adherence monitoring.
- **Daily Health Check-ins:** Allows patients to report symptoms and manually enter vital signs.
- **Risk Prediction:** Combines safety rules and machine learning to identify potential risks.
- **Clinician Dashboard:** Displays patient risk levels, alerts, adherence statistics, and recovery trends.

## 4. System Workflow

Discharge Summary
       |
       v
Information Extraction
       |
       v
Structured Recovery Plan
       |
       v
Task Scheduling & Reminders
       |
       v
Daily Check-ins & Vitals
       |
       v
Risk Detection
(Safety Rules + ML Model)
       |
       v
Clinician Dashboard
```

****5. Technology Stack****

Python- Backend development
Streamlit- User interface and dashboard
SQLite- Database
Pandas- Data processing
Scikit-learn- Machine learning
NLP / Rule-based Extraction- Discharge summary processing
SHAP- Model explainability
Matplotlib- Data visualisation
Git & GitHub- Version control

## 6. Project Structure

PostCare-Companion/
│
├── README.md
├── requirements.txt
├── schema.json
│
├── data/
├── docs/
├── notebooks/
│
├── src/
│   ├── extraction/
│   ├── plan/
│   ├── risk/
│   ├── app/
│   └── simulate_vitals.py
│
├── models/
├── logs/
└── tests/


## 7. Installation and Execution

**Clone the repository**
git clone <github.com/manasvini-sringeri/medicore>
cd PostCare-Companion


**Create a virtual environment**
python -m venv venv

**Activate the environment (Windows)**
venv\Scripts\activate

**Install dependencies**
pip install -r requirements.txt

**Run the application**

streamlit run src/app/main.py
```

## 8. Machine Learning Approach

The risk prediction module estimates the probability of hospital readmission to support patient monitoring.

- Models: Logistic Regression and Gradient Boosting.
- Evaluation: AUROC, AUPRC, Sensitivity, Specificity, and Calibration.
- Explainability: SHAP-based feature importance.

The final risk classification combines machine learning predictions with clinician-reviewed safety rules. Safety rules take priority over ML predictions.

## 9. Data and Privacy

- Uses synthetic and open-access datasets.
- No real patient data is used.
- Synthetic discharge summaries are used for extraction testing.
- Simulated vital signs are used for demonstration.
- Extracted recovery instructions require human confirmation before activation.

## 10. Limitations and Future Scope

**Current Limitations**
- Limited synthetic discharge summary testing.
- English text input only.
- Manual vital-sign entry.
- Limited clinical review and no clinical validation.

**Future Enhancements**
- OCR for scanned discharge summaries.
- Regional language and voice support.
- Hospital system integration.
- Wearable device integration.
- Clinical validation with appropriate ethics approval.
