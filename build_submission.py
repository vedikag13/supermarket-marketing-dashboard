from pathlib import Path
import csv, math, shutil
from collections import Counter, defaultdict
from statistics import median
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

ROOT = Path(__file__).parent
OUT = ROOT / 'submission'
OUT.mkdir(exist_ok=True)
SRC = Path(r'C:\Users\Aryan\Downloads\Learning_Centre_Survey_Dataset_SAMPLE.xlsx')
DOCX_GUIDE = Path(r'C:\Users\Aryan\Downloads\Project based Learning Individual and Group Project (1).docx')

# The source workbook states that its 250 rows are fake sample data. Preserve this warning.
srcwb = load_workbook(SRC, read_only=True, data_only=True)
ws = srcwb['Responses']
headers = [c.value for c in ws[1]]
records = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=2, values_only=True)]

# Clean: retain respondent records, remove duplicate IDs, coerce columns by their declared role,
# impute missing numeric/categorical predictors, drop unusable geographies, flag source gaps.
dedup = {r['respondent_id']: r for r in records if r.get('respondent_id') is not None}
records = list(dedup.values())
numeric = [h for h in headers if h not in ('respondent_id','locality','pincode','board','trial_interest')]
cat = ['board','trial_interest']
for h in numeric:
    vals = [float(r[h]) for r in records if isinstance(r.get(h),(int,float))]
    fill = median(vals) if vals else 0
    for r in records:
        if not isinstance(r.get(h),(int,float)): r[h] = fill
        else: r[h] = float(r[h])
for h in cat:
    counts = Counter(r[h] for r in records if r.get(h) not in (None,''))
    fill = counts.most_common(1)[0][0] if counts else 'Unknown'
    for r in records:
        if r.get(h) in (None,''): r[h] = fill

# Normalize encoded fields to integer where possible; retain all input fields and add transparent flags.
out_headers = headers + ['geo_available','source_is_synthetic','high_enrol_intent']
for r in records:
    r['geo_available'] = int(bool(r.get('locality')) and bool(r.get('pincode')))
    r['source_is_synthetic'] = 1
    r['high_enrol_intent'] = int(r['enrol_intent'] in (4,5))
    for h in numeric:
        r[h] = round(float(r[h]), 2)

csv_path = OUT/'learning_centre_survey_cleaned.csv'
with csv_path.open('w',newline='',encoding='utf-8-sig') as f:
    wr=csv.DictWriter(f,fieldnames=out_headers); wr.writeheader(); wr.writerows(records)

# Dataset workbook with source provenance and clear codebook.
wb=Workbook(); data=wb.active; data.title='Cleaned Data'
data.append(out_headers)
for r in records: data.append([r.get(h) for h in out_headers])
readme=wb.create_sheet('Read Me')
for row in [
 ['Learning Centre Survey Dataset'],
 ['Provenance','Derived from the supplied Learning_Centre_Survey_Dataset_SAMPLE.xlsx Responses sheet.'],
 ['Data status','Synthetic / fake sample data as stated in the supplied workbook. Not evidence from real parents.'],
 ['Unit of observation','One parent survey response (250 rows after duplicate-ID removal).'],
 ['Cleaning','Removed duplicate respondent IDs; median-imputed numeric blanks; mode-imputed board/trial_interest; retained blank locality and pincode; added flags.'],
 ['Geography','All locality and PIN code fields are blank in the source. geo_available=0; no locality analysis is possible.'],
 ['Targets','wtp_one_subject is monthly willingness to pay in INR. high_enrol_intent=1 for enrol_intent 4 or 5.'],
 ['Use','Replace with consented, real parent survey data before making launch, pricing or site decisions.'],
]: readme.append(row)
code=wb.create_sheet('Data Dictionary'); code.append(['Column','Definition / coding'])
for h in out_headers:
    code.append([h, 'Source survey field. See supplied Codebook sheet; added field.' if h in headers else {'geo_available':'1 if locality and PIN code both present; else 0','source_is_synthetic':'Always 1 for this sample','high_enrol_intent':'1 when enrol_intent is 4 or 5; else 0'}[h]])
for sh in wb.worksheets:
    sh.freeze_panes='A2'; sh.auto_filter.ref=sh.dimensions
    for c in sh[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='17365D'); c.alignment=Alignment(wrap_text=True,vertical='center')
    sh.row_dimensions[1].height=28
    for col in sh.columns:
        letter=get_column_letter(col[0].column); maxlen=max((len(str(x.value or '')) for x in col[:100]),default=10)
        sh.column_dimensions[letter].width=min(max(maxlen+2,12),48)
dataset_xlsx=OUT/'learning_centre_survey_dataset.xlsx'; wb.save(dataset_xlsx)

# Summary calculations for report.
fees=[r['wtp_one_subject'] for r in records]; spend=[r['current_spend'] for r in records]
interest=[r['interest'] for r in records]; trials=[r['trial_interest'] for r in records]
income_map={1:'Under ₹25k',2:'₹25k–50k',3:'₹50k–1L',4:'₹1–2L',5:'Over ₹2L'}
by_income=defaultdict(list)
for r in records: by_income[r['income_band']].append(r['wtp_one_subject'])
interest_pct=sum(x>=4 for x in interest)/len(interest)
trial_pct=sum(x=='Yes' for x in trials)/len(trials)
high_intent_pct=sum(r['high_enrol_intent'] for r in records)/len(records)

# Report document.
doc=Document(); sec=doc.sections[0]; sec.top_margin=Inches(.72); sec.bottom_margin=Inches(.65); sec.left_margin=Inches(.78); sec.right_margin=Inches(.78)
styles=doc.styles; styles['Normal'].font.name='Aptos'; styles['Normal'].font.size=Pt(9.5); styles['Normal'].font.color.rgb=RGBColor(45,55,68)
for nm,size,col in [('Title',26,'17365D'),('Heading 1',16,'17365D'),('Heading 2',11,'2878A5')]:
 s=styles[nm]; s.font.name='Aptos Display'; s.font.size=Pt(size); s.font.bold=True; s.font.color.rgb=RGBColor.from_string(col)
p=doc.add_paragraph(style='Title'); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run('Activity Based Learning Centre Business Analysis')
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; rr=p.add_run('English and mathematics for Classes 1 to 8 | Individual project report'); rr.bold=True; rr.font.size=Pt(12)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run('Prepared from the supplied sample survey and project brief | Data analytics and Streamlit dashboard')
def h(t,l=1): doc.add_heading(t,level=l)
def para(t): doc.add_paragraph(t)
def table(headers_, rows, widths=None):
 t=doc.add_table(rows=1, cols=len(headers_)); t.style='Light Shading Accent 1'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
 for c,x in zip(t.rows[0].cells,headers_): c.text=str(x)
 for row in rows:
  cells=t.add_row().cells
  for c,x in zip(cells,row): c.text=str(x); c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
 return t

h('Abstract')
para(f'This project evaluates a proposed physical learning centre where children in Classes 1–8 learn English and mathematics through activity-based sessions. The analysis uses the supplied 250-row parent survey sample. Its source workbook labels the responses as fake data generated for testing, so the results demonstrate an analytics workflow and do not establish demand, learning impact, or willingness to pay among real families. The prepared dataset, cleaning logic, Streamlit code, algorithm comparisons, and dashboard images are included with this report. The synthetic sample indicates a median stated fee of ₹{median(fees):,.0f} per subject per month and {interest_pct:.0%} with interest scores of 4–5. These figures are useful only to test the pipeline. A consented local pilot is required before choosing fees, centres, or staffing.')
h('Introduction and business idea')
para('The business idea is to offer in-person English and mathematics learning for children in Classes 1–8, grouped by demonstrated skill level (beginner, intermediate, advanced) rather than age alone. Sessions would use games, projects, discussion, manipulatives, reading, and problem solving. The proposition responds to a parent concern about rote learning while keeping foundational skills and regular progress checks visible.')
para('The initial business questions are whether parents show interest, what monthly fee range merits a real price test, which family segments express different needs, and what operational evidence is needed before opening a centre. Any European approach is a design inspiration, not a claim that all European schools teach alike or that a method will transfer unchanged to Indian contexts.')
h('Objectives')
for t in ['Describe the survey sample and identify data quality gaps.','Explore relationships among interest, stated fee, income, current tuition spending, and learning preferences.','Demonstrate fee regression, enrolment-intent classification, K-NN, tree/ensemble models, clustering, and association-rule analysis.','Translate findings into a staged, measurable pilot plan.']: doc.add_paragraph(t,style='List Bullet')
h('Dataset and domain')
para('The source dataset contains 250 parent-response rows and 29 fields covering child class, school board and fee tier, income band, current tuition spending, learning beliefs, interest, trial interest, stated willingness to pay, tested price, enrolment intent, and four Van Westendorp price questions. Locality and PIN code are blank in the supplied sample. The unit is one parent response; no learning outcomes, attendance, retention, actual payment, or child assessment records are provided.')
table(['Item','Value / interpretation'],[['Rows after deduplication',len(records)],['Median willingness to pay, one subject / month',f'₹{median(fees):,.0f} (synthetic sample)'],['Median existing tuition spend / month',f'₹{median(spend):,.0f}'],['Interest score 4 or 5',f'{interest_pct:.1%}'],['Trial interest = Yes',f'{trial_pct:.1%}'],['High enrolment intent (score 4–5)',f'{high_intent_pct:.1%}'],['Geography usable',f'{sum(r["geo_available"] for r in records)} rows']])
h('Data cleaning and transformation')
para('The pipeline removes duplicate respondent IDs, converts numeric survey fields to numeric values, imputes missing numeric values with the column median and missing board/trial responses with the mode, and keeps blank geography blank. It adds geo_available, source_is_synthetic, and high_enrol_intent fields. No row is discarded for missing locality, because geography is not required for the pricing or intent demonstrations. The source workbook and this exported dataset retain a clear fake-data warning.')
para('Before using a live survey, validate ranges, remove test submissions, document consent, prevent duplicate households, inspect missingness, and retain a data dictionary. The current sample has no usable PIN codes, so site selection cannot be inferred. Synthetic values can also encode artificial relationships that inflate model fit.')
h('Framework and rationale for techniques')
table(['Technique','Target / purpose','Rationale and caution'],[
 ['Descriptive and diagnostic EDA','Distribution and bivariate relationships','Summarizes stated preferences and spots data gaps; correlation is not causation.'],
 ['Linear regression','wtp_one_subject (INR/month)','Directly models a continuous fee outcome; coefficients are associations in synthetic data.'],
 ['Ridge and Lasso regression','Same fee outcome','Regularization reduces unstable coefficients when predictors are correlated; tune inside cross-validation.'],
 ['Classification: logistic, K-NN, decision tree, random forest, gradient boosting, SVM, Naive Bayes','high_enrol_intent (score 4 or 5)','Compares interpretable and nonlinear models using stratified holdout and cross-validation; 250 fake rows are too few for deployment.'],
 ['K-Means clustering','Standardized family / preference fields','Explores segments without a label; cluster numbers are descriptive, not established customer types.'],
 ['Association rules','Discretized preference and family attributes','Finds co-occurrence patterns for hypotheses; support/confidence are not causal evidence.']])
h('Exploratory findings')
para(f'The synthetic sample has a median stated one-subject fee of ₹{median(fees):,.0f} per month. {interest_pct:.0%} report an interest score of 4–5 and {trial_pct:.0%} say they want a free trial. Those are survey intentions and may overstate real conversion. The source dashboard suggests testing price points rather than treating any stated fee as a recommended launch price; it reports an acceptable band of ₹1,750–₹4,500 and a test-point revenue index that peaks at ₹3,000. This is a scenario from the fake sample, not a business forecast.')
rows=[]
for k in sorted(by_income): rows.append([income_map.get(int(k),str(k)),len(by_income[k]),f'₹{median(by_income[k]):,.0f}'])
table(['Income band','Responses','Median fee'],rows)
para('The sample summary shows willingness to pay rising with income bands. A real analysis should report uncertainty, ensure adequate group sizes, and test whether the pattern remains after controls. In the source dashboard, a multivariable regression reports positive associations for income, school-fee tier, interest, and rote-learning concern; because the dataset is fake, these coefficients should be treated as demonstration output only.')
h('Algorithmic analysis and evaluation plan')
para('For fee estimation, the code fits ordinary least squares plus Ridge and Lasso. Report R², MAE, and RMSE on held-out data; compare with a median-only baseline and inspect residuals. For intent, it compares logistic regression, K-NN, decision tree, random forest, gradient boosting, support vector machine, and Gaussian Naive Bayes. Report accuracy, precision, recall, F1, and ROC-AUC, with the positive class defined as intent score 4 or 5. Use stratified cross-validation, scaling for distance-based and margin-based models, and a fixed random seed. The sample is small and synthetic, so metrics are not generalizable. The dashboard computes these comparisons when run with the listed requirements.')
para('K-NN is a natural classroom-level placement demonstration only after real diagnostic scores exist. It assigns a new child based on nearby assessed students, but depends on meaningful feature scaling, enough examples across levels, and a validated placement rubric. Parent survey rows are not student assessment records. The current survey is therefore not suitable for recommending a child’s learning level.')
para('K-Means and association rules are exploratory. Choose the number of clusters using silhouette score and inspect cluster profiles before assigning names. Mine itemsets from discretized attributes and filter rules by support and confidence; a minimum lift above 1 indicates co-occurrence above the independence baseline, not a causal effect. Geographic clusters are unavailable because locality fields are blank.')
h('What is working and what is not working')
table(['Working in the concept','Needs validation or redesign'],[
 ['Clear age span and two core subjects support a focused first pilot.','Classes 1–8 is wide; curricula, session length, and class-size limits should vary by grade band.'],
 ['Activity-based learning provides a testable alternative to worksheet-only tuition.','No sample evidence measures skill gain, engagement, or retention. Use pre/post assessments and attendance.'],
 ['Three skill levels create a possible pathway for differentiated instruction.','Do not place children using survey data or a model trained on parent responses. Use a teacher-reviewed diagnostic.'],
 ['A free trial and price experiment are easy to pilot.','Interest and stated willingness to pay do not establish paid conversion or unit economics.'],
 ['The survey includes family spending, income bands, and learning preferences.','Synthetic rows and missing geography cannot justify pricing, demand, or site choice.']])
h('Recommendations and pilot design')
for t in ['Run a real, consented parent survey in the target catchment. Capture locality/PIN code, preferred schedule, subject mix, class size, accessibility needs, trial booking, and a specific price offer.','Test one small centre before committing to multiple sites. Offer a short free/low-cost trial and track inquiry-to-trial, trial-to-paid conversion, attendance, renewal, acquisition cost, rent, teacher utilization, and contribution margin.','Assess each learner at entry and at regular intervals in English and mathematics. Let trained teachers review initial placement and level changes.','Build an activity bank mapped to grade-specific outcomes. Keep lesson plans, materials, teacher training, and safeguarding procedures consistent across levels.','Compare price offers with randomized or sequential tests and actual paid enrolment. Report conversion and confidence intervals by catchment and grade band.','Only after accumulating real student records, evaluate placement models. Split by child and time to prevent leakage; compare K-NN with transparent rubric and teacher decisions. Use fairness and error checks before any placement support.']: doc.add_paragraph(t,style='List Number')
h('Conclusion')
para('The idea is testable as a small, local learning-centre pilot. The supplied files support a reproducible analytics demonstration, but their synthetic sample cannot validate market demand or learning effectiveness. The strongest next step is to collect genuine local survey and pilot data, define success measures, and use teacher-led assessment before applying predictive models to children. The Streamlit dashboard, cleaned dataset, source code, and screenshot files accompany this report.')
h('Appendix and deliverables')
para('The submission folder includes the Streamlit application, requirements file, cleaned dataset in Excel and CSV formats, and dashboard screenshots. The Excel file contains Cleaned Data, Read Me, and Data Dictionary sheets. To run the dashboard, install requirements and run: streamlit run app.py. See README.txt for details.')
# footer with page numbers
for s in doc.sections:
    f=s.footer.paragraphs[0]; f.alignment=WD_ALIGN_PARAGRAPH.CENTER; f.add_run('Learning Centre Business Analysis | Synthetic data demonstration')
doc.save(OUT/'learning_centre_business_analysis_report.docx')

print('rows',len(records),'median_fee',median(fees),'interest',interest_pct,'trial',trial_pct,'high_intent',high_intent_pct)
