from pathlib import Path
from docx import Document

p=Path(__file__).parent/'learning_centre_business_analysis_report.docx'
d=Document(p)
for para in d.paragraphs:
    if para.text.startswith('For fee estimation, the code fits'):
        para.text=('For fee estimation, the code fits ordinary least squares plus Ridge and Lasso. '
                   'Report R², MAE, and RMSE on held-out data; compare with a median-only baseline and inspect residuals. '
                   'For intent, it compares logistic regression, K-NN, decision tree, random forest, gradient boosting, support vector machine, and Gaussian Naive Bayes. '
                   'The positive class is intent score 4 or 5. The dashboard uses a fixed, stratified 75/25 holdout split and reports accuracy, precision, recall, F1, and ROC-AUC. '
                   'For real data, tune models inside stratified cross-validation and compare against simple baselines. '
                   'The sample is small and synthetic, so its holdout metrics are not generalizable. The dashboard computes these comparisons when run with the listed requirements.')
    if para.text.startswith('K-Means and association rules are exploratory.'):
        para.text=('K-Means and association rules are exploratory. Choose the number of clusters using silhouette score and inspect cluster profiles before assigning names. '
                   'The dashboard groups discretized preference attributes into pairs and reports support, confidence, and lift, sorted by lift. '
                   'Lift above 1 indicates co-occurrence above the independence baseline, not a causal effect. Geographic clusters are unavailable because locality fields are blank.')
d.save(p)
print('aligned report to implemented dashboard')
