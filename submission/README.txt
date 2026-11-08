LEARNING CENTRE ANALYTICS SUBMISSION

FILES
- learning_centre_business_analysis_report.docx: project report and business diagnosis
- app.py: interactive Streamlit dashboard and model comparison code
- requirements.txt: Python packages used by the dashboard
- learning_centre_survey_dataset.xlsx: cleaned dataset, Read Me and Data Dictionary sheets
- learning_centre_survey_cleaned.csv: CSV input used by the dashboard
- dashboard_screenshots/: visual dashboard previews based on the synthetic sample

RUN THE DASHBOARD
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run: python -m venv .venv
4. Activate the environment, then run: pip install -r requirements.txt
5. Run: streamlit run app.py

IMPORTANT DATA NOTE
The supplied workbook itself labels all 250 responses as fake sample data generated for testing.
The output files retain that warning. Do not make pricing, site, hiring, or child-placement
decisions from these rows. Replace the CSV with consented real survey data for market analysis.
Locality and PIN code are blank in the supplied sample. K-NN for placement is discussed as a
future use case; the current model comparison predicts survey enrolment intent only.
