"""Render the actual values displayed by the live dashboard's default sample run."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

out=Path(__file__).parent/'dashboard_screenshots'/'03_live_model_results.png'
W,H=1440,1120; im=Image.new('RGB',(W,H),'#EEF4F7'); d=ImageDraw.Draw(im)
def f(sz,b=False):
    p=r'C:\Windows\Fonts\segoeuib.ttf' if b else r'C:\Windows\Fonts\segoeui.ttf'
    try:return ImageFont.truetype(p,sz)
    except:return ImageFont.load_default()
navy='#14324B'; blue='#2F78A5'; white='#FFFFFF'; ink='#263746'; muted='#5D6B75'; warn='#FFF0D3'
d.rectangle((0,0,W,72),fill=navy); d.text((40,22),'LEARNING CENTRE  /  ALGORITHM COMPARISON',font=f(22,True),fill=white)
d.text((40,94),'Live dashboard model results',font=f(31,True),fill=navy)
d.rounded_rectangle((40,146,1400,195),radius=10,fill='#F5D8A5'); d.text((60,162),'SYNTHETIC SAMPLE · 250 fake rows · One stratified 75/25 holdout · Not decision evidence',font=f(18,True),fill='#634B1D')

def table(x,y,w,title,cols,rows,widths):
    d.rounded_rectangle((x,y,x+w,y+20+36*(len(rows)+1)+55),radius=12,fill=white,outline='#D5E0E6',width=2)
    d.text((x+20,y+16),title,font=f(22,True),fill=navy)
    yy=y+58; d.rectangle((x+16,yy,x+w-16,yy+38),fill=navy)
    xx=x+26
    for c,ww in zip(cols,widths):d.text((xx,yy+10),c,font=f(14,True),fill=white); xx+=ww
    yy+=38
    for i,row in enumerate(rows):
        d.rectangle((x+16,yy,x+w-16,yy+36),fill='#F2F6F8' if i%2==0 else white)
        xx=x+26
        for val,ww in zip(row,widths):d.text((xx,yy+9),str(val),font=f(14),fill=ink); xx+=ww
        yy+=36

table(40,220,650,'Fee regression',['Model','R²','MAE ₹','RMSE ₹'],[
 ['Linear','0.817','407','509'],['Ridge','0.816','411','510'],['Lasso','0.815','410','512']], [170,100,130,130])
table(710,220,690,'Enrolment intent classification',['Model','Acc.','Prec.','Recall','F1','AUC'],[
 ['Logistic','0.698','0.742','0.676','0.708','0.734'],['K-NN','0.556','0.600','0.529','0.562','0.593'],['Decision tree','0.524','0.545','0.706','0.615','0.550'],['Random forest','0.651','0.667','0.706','0.686','0.667'],['Gradient boost','0.571','0.590','0.676','0.630','0.657'],['SVM','0.667','0.710','0.647','0.677','0.708'],['Naive Bayes','0.730','0.743','0.765','0.754','0.742']], [140,75,75,80,70,70])
d.rounded_rectangle((40,650,1400,744),radius=12,fill=white,outline='#D5E0E6',width=2)
d.text((60,666),'Unsupervised and pattern analysis',font=f(20,True),fill=navy)
d.text((60,704),'K-Means: k = 3, silhouette = 0.19 (weak separation)',font=f(16),fill=ink)
d.text((730,704),'Top association pair: high interest + rote concern · support 0.13 · confidence 0.33 · lift 1.54',font=f(15),fill=ink)
d.rounded_rectangle((40,770,1400,895),radius=12,fill=warn)
d.text((62,792),'Interpretation',font=f(18,True),fill='#634B1D')
d.text((62,823),'Linear regression edges Ridge/Lasso by a small margin. Naive Bayes leads this holdout; K-NN is weaker.',font=f(16),fill=ink)
d.text((62,851),'The synthetic dataset and single holdout cannot support real pricing, marketing, or student placement decisions.',font=f(16),fill=ink)
d.text((40,930),'Metrics reproduced from the running Streamlit app. Replace the fake sample with consented local survey and student data.',font=f(16),fill=muted)
im.save(out); print(out)
