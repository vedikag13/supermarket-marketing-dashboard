from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

root=Path(__file__).parent
src=load_workbook(r'C:\Users\Aryan\Downloads\Learning_Centre_Survey_Dataset_SAMPLE.xlsx',read_only=True,data_only=True)
definitions={}
for row in src['Codebook'].iter_rows(min_row=2,values_only=True):
    if row[0]: definitions[row[0]]=f'{row[1] or ""} Coding: {row[2] or ""}'.strip()
definitions.update({
 'geo_available':'Added cleaning flag. 1 when both locality and PIN code are present; otherwise 0.',
 'source_is_synthetic':'Added provenance flag. Always 1 because all rows in this supplied sample are labelled fake.',
 'high_enrol_intent':'Added modelling target. 1 when enrol_intent is 4 or 5; otherwise 0.',
})
path=root/'learning_centre_survey_dataset.xlsx'; wb=load_workbook(path)
ws=wb['Data Dictionary']; ws.delete_rows(1,ws.max_row); ws.append(['Column','Definition / coding'])
for h in [c.value for c in wb['Cleaned Data'][1]]: ws.append([h,definitions.get(h,'Source survey field; see original sample codebook.')])
for c in ws[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='17365D'); c.alignment=Alignment(wrap_text=True,vertical='center')
ws.column_dimensions['A'].width=30; ws.column_dimensions['B'].width=100; ws.freeze_panes='A2'; ws.auto_filter.ref=ws.dimensions
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment=Alignment(wrap_text=True,vertical='top')
wb.save(path)
print('updated dictionary',ws.max_row-1,'fields')
