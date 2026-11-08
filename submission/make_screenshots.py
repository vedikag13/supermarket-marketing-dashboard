"""Create static dashboard preview images for the submission bundle."""
from pathlib import Path
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).parent; OUT=HERE/'dashboard_screenshots'; OUT.mkdir(exist_ok=True)
df=pd.read_csv(HERE/'learning_centre_survey_cleaned.csv')
W,H=1440,900
navy='#14324B'; blue='#2F78A5'; pale='#EEF4F7'; ink='#263746'; muted='#5D6B75'; orange='#F5D8A5'; white='#FFFFFF'; teal='#3E9B8F'
def font(size,bold=False):
    candidates=[r'C:\Windows\Fonts\segoeuib.ttf' if bold else r'C:\Windows\Fonts\segoeui.ttf',r'C:\Windows\Fonts\arial.ttf']
    for p in candidates:
        try:return ImageFont.truetype(p,size)
        except:pass
    return ImageFont.load_default()
def base(tab):
    im=Image.new('RGB',(W,H),pale); d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,76),fill=navy); d.text((42,20),'LEARNING CENTRE',font=font(23,True),fill=white); d.text((1060,26),tab,font=font(18,True),fill='#D8E8F0')
    d.text((40,99),'Business and Survey Dashboard',font=font(32,True),fill=navy)
    d.text((42,140),'Activity-based English and Mathematics  |  Classes 1–8  |  Parent survey',font=font(17),fill=muted)
    d.rounded_rectangle((40,177,1400,229),radius=10,fill=orange)
    d.text((58,192),'SYNTHETIC SAMPLE DATA: 250 fake test rows. Not evidence of real parent demand or pricing.',font=font(18,True),fill='#634B1D')
    return im,d
def card(d,x,y,w,label,value,sub):
    d.rounded_rectangle((x,y,x+w,y+128),radius=13,fill=white,outline='#D5E0E6',width=2)
    d.text((x+18,y+16),label,font=font(16,True),fill=muted); d.text((x+18,y+45),value,font=font(30,True),fill=navy); d.text((x+18,y+91),sub,font=font(14),fill=muted)
fee=df.wtp_one_subject; int_pct=(df.interest>=4).mean(); tr_pct=(df.trial_interest=='Yes').mean(); high=(df.high_enrol_intent==1).mean()
im,d=base('MARKET SIGNALS')
for x,l,v,s in [(40,'SURVEY RESPONSES',str(len(df)),'synthetic rows'),(385,'MEDIAN STATED FEE',f'Rs {fee.median():,.0f}','per subject / month'),(730,'HIGH INTEREST',f'{int_pct:.0%}','interest score 4 or 5'),(1075,'FREE TRIAL: YES',f'{tr_pct:.0%}','reported interest')]: card(d,x,250,320,l,v,s)
d.rounded_rectangle((40,399,690,835),radius=13,fill=white,outline='#D5E0E6',width=2)
d.text((64,419),'Median stated fee by income band',font=font(21,True),fill=navy)
groups=df.groupby('income_band').wtp_one_subject.median()
labels=['Under 25k','25k–50k','50k–1L','1–2L','Over 2L']; maxv=max(groups)
for i,(lab,val) in enumerate(zip(labels,groups.sort_index())):
    y=485+i*61; d.text((64,y),lab,font=font(15),fill=ink); d.rounded_rectangle((190,y+2,600,y+30),radius=7,fill='#E5EDF2'); d.rounded_rectangle((190,y+2,190+int(410*val/maxv),y+30),radius=7,fill=blue); d.text((615,y+4),f'Rs {val:,.0f}',font=font(15,True),fill=navy)
d.rounded_rectangle((720,399,1400,835),radius=13,fill=white,outline='#D5E0E6',width=2)
d.text((744,419),'Business diagnosis',font=font(21,True),fill=navy)
lines=['What looks promising','• English and maths focus is clear','• Activity-led sessions are testable','• A trial can measure conversion','',"What is not established",'• Sample responses are synthetic','• Locality and PIN code are blank','• No learning or retention outcomes','',f'High intent (score 4–5): {high:.0%}','Survey intent is not paid enrolment.']
y=466
for line in lines:
    d.text((746,y),line,font=font(16,line in ('What looks promising','What is not established')),fill=teal if line.startswith('What') else ink); y+=29
im.save(OUT/'01_market_signals.png')

im,d=base('ALGORITHM COMPARISON')
d.rounded_rectangle((40,250,1400,828),radius=13,fill=white,outline='#D5E0E6',width=2)
d.text((64,274),'Models available in the interactive Streamlit app',font=font(23,True),fill=navy)
d.text((64,316),'The app computes held-out metrics after you install requirements and run it.',font=font(17),fill=muted)
cols=[64,365,760,1080]; d.rectangle((60,365,1380,407),fill=navy)
for x,txt in zip(cols,['Model family','Business question','Evaluation','Data status']):d.text((x,376),txt,font=font(16,True),fill=white)
rows=[('Linear / Ridge / Lasso','Monthly fee estimate','R², MAE, RMSE','Parent survey'),('Logistic regression','High enrolment intent','Accuracy, precision, recall, F1, AUC','Parent survey'),('K-NN','High enrolment intent demo','Accuracy, precision, recall, F1, AUC','Parent survey'),('Decision tree / Random forest','High enrolment intent','Accuracy, precision, recall, F1, AUC','Parent survey'),('Gradient boosting / SVM / Naive Bayes','High enrolment intent','Accuracy, precision, recall, F1, AUC','Parent survey'),('K-Means','Exploratory family segments','Silhouette score','Parent survey'),('Association pairs','Co-occurring preferences','Support, confidence, lift','Parent survey')]
y=407
for i,row in enumerate(rows):
    fill='#F2F6F8' if i%2==0 else white; d.rectangle((60,y,1380,y+57),fill=fill)
    for x,txt in zip(cols,row):d.text((x,y+17),txt,font=font(15),fill=ink)
    y+=57
d.rounded_rectangle((64,829,1376,866),radius=8,fill='#FFF0D3')
d.text((82,838),'K-NN is not a student placement model here. Real diagnostic scores and teacher review are required.',font=font(16,True),fill='#634B1D')
im.save(OUT/'02_algorithm_comparison.png')
print('saved',*(p.name for p in OUT.glob('*.png')))
