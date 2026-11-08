from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root=Path(__file__).parent
report=root/'learning_centre_business_analysis_report.docx'
replacement=root/'dashboard_screenshots'/'03_live_model_results.png'
temp=root/'learning_centre_business_analysis_report.tmp.docx'
with ZipFile(report,'r') as src, ZipFile(temp,'w',ZIP_DEFLATED) as dst:
    for item in src.infolist():
        payload=replacement.read_bytes() if item.filename=='word/media/image3.png' else src.read(item.filename)
        dst.writestr(item,payload)
temp.replace(report)
print('refreshed embedded live model results image')
