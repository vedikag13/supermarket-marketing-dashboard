from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

root=Path(__file__).parent
p=root/'learning_centre_business_analysis_report.docx'; d=Document(p)
ref=next(x for x in d.paragraphs if x.text=='What is working and what is not working')
def paragraph_before(text,style='Normal'):
    x=d.add_paragraph(text,style=style); ref._p.addprevious(x._p); return x
def table_before(headers,rows):
    t=d.add_table(rows=1,cols=len(headers)); t.style='Light Shading Accent 1'
    for c,v in zip(t.rows[0].cells,headers): c.text=v
    for row in rows:
        cells=t.add_row().cells
        for c,v in zip(cells,row): c.text=str(v)
    ref._p.addprevious(t._tbl); return t

paragraph_before('Results from the sample run','Heading 1')
paragraph_before('The Streamlit dashboard was launched with the included 250-row synthetic dataset. These values come from one 75/25 holdout split with a fixed random seed. The results demonstrate the workflow and should not be generalized to real families.')
paragraph_before('Fee prediction results','Heading 2')
table_before(['Model','R²','MAE ₹','RMSE ₹'],[
 ['Linear regression','0.817','407','509'],['Ridge','0.816','411','510'],['Lasso','0.815','410','512']])
paragraph_before('Linear regression performed marginally better on this holdout, while Ridge and Lasso were very close. The small differences do not establish a preferred pricing model; evaluate repeated cross-validation and real survey data before use.')
paragraph_before('Enrolment intent classification','Heading 2')
table_before(['Model','Accuracy','Precision','Recall','F1','ROC-AUC'],[
 ['Logistic regression','0.698','0.742','0.676','0.708','0.734'],
 ['K-NN','0.556','0.600','0.529','0.562','0.593'],
 ['Decision tree','0.524','0.545','0.706','0.615','0.550'],
 ['Random forest','0.651','0.667','0.706','0.686','0.667'],
 ['Gradient boosting','0.571','0.590','0.676','0.630','0.657'],
 ['SVM','0.667','0.710','0.647','0.677','0.708'],
 ['Naive Bayes','0.730','0.743','0.765','0.754','0.742']])
paragraph_before('Naive Bayes had the highest accuracy, F1, and ROC-AUC on this split. K-NN performed less well. The target is parent survey intent (score 4–5), not child learning level. These scores are sample-specific and provide no basis for targeting real parents or placing students.')
paragraph_before('Other methods','Heading 2')
paragraph_before('With three K-Means clusters, the silhouette score was 0.19, indicating weakly separated groups. The highest-lift association pair was high interest with high rote-learning concern (support 0.13, confidence 0.33, lift 1.54). It is a low-support co-occurrence in fake data, not a causal finding. The sample has no usable locality or PIN code for geographic clustering.')

# Append the results snapshot after the original two appendix figures.
d.add_page_break()
d.add_heading('Live model results screenshot',level=1)
p0=d.add_paragraph('Captured values from the interactive dashboard running on the supplied synthetic sample.'); p0.paragraph_format.space_after=Pt(8)
d.add_picture(str(root/'dashboard_screenshots'/'03_live_model_results.png'),width=Inches(6.85))
cap=d.add_paragraph('Figure 3. Regression, classification, clustering, and association results'); cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
d.save(p)
print('added executed model results and screenshot')
