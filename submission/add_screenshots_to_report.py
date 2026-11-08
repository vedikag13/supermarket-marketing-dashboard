from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

root=Path(__file__).parent
path=root/'learning_centre_business_analysis_report.docx'
doc=Document(path)
doc.add_page_break()
doc.add_heading('Dashboard screenshots',level=1)
p=doc.add_paragraph('These dashboard previews use the supplied synthetic sample. The interactive dashboard computes the model metrics when run with the listed Python requirements.')
p.paragraph_format.space_after=Pt(10)
for filename,caption in [
 ('01_market_signals.png','Figure 1. Market signals and business diagnosis'),
 ('02_algorithm_comparison.png','Figure 2. Algorithm comparison available in the Streamlit dashboard'),
]:
    doc.add_picture(str(root/'dashboard_screenshots'/filename),width=Inches(6.85))
    p=doc.add_paragraph(caption); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after=Pt(14)
doc.save(path)
print('updated report with 2 dashboard images')
