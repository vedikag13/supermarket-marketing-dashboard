"""Activity-based learning centre dashboard.

Run: streamlit run app.py
The bundled sample is synthetic. Replace the CSV with consented survey data before decisions.
"""
from pathlib import Path
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, RidgeCV, LassoCV, LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, mean_absolute_error, mean_squared_error, r2_score)
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

st.set_page_config(page_title='Learning Centre Dashboard', page_icon='📚', layout='wide')
DATA = Path(__file__).with_name('learning_centre_survey_cleaned.csv')
st.title('Learning Centre | Business and Survey Dashboard')
st.caption('Activity-based English and mathematics · Classes 1–8 · Parent survey analysis')
st.error('SYNTHETIC SAMPLE DATA: these 250 rows are fake test data. They do not establish real demand, pricing, learning impact, or centre locations.')

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

uploaded=st.sidebar.file_uploader('Optional: upload a replacement survey CSV',type='csv')
df=load_data(uploaded) if uploaded else load_data(DATA)
if 'child_class' not in df or 'wtp_one_subject' not in df:
    st.error('The CSV needs the original survey columns. See the Read Me and Data Dictionary sheets.'); st.stop()
class_sel=st.sidebar.multiselect('Child class',sorted(df.child_class.dropna().unique()),default=sorted(df.child_class.dropna().unique()))
view=df[df.child_class.isin(class_sel)]
if view.empty: st.warning('Select at least one class.'); st.stop()

fee=view.wtp_one_subject.dropna()
interest=view.interest.dropna()
trial=(view.trial_interest.astype(str).str.lower()=='yes').mean()
c1,c2,c3,c4=st.columns(4)
c1.metric('Survey responses',f'{len(view):,}')
c2.metric('Median stated fee / subject',f'₹{fee.median():,.0f}')
c3.metric('Interest score 4–5',f'{(interest>=4).mean():.0%}')
c4.metric('Free trial: Yes',f'{trial:.0%}')

tab1,tab2,tab3,tab4=st.tabs(['Market signals','Algorithm comparison','Segments and patterns','Business diagnosis'])
with tab1:
    left,right=st.columns(2)
    with left:
        st.subheader('Stated fee by household income')
        summary=view.groupby('income_band',dropna=False).wtp_one_subject.agg(['median','count']).reset_index()
        fig,ax=plt.subplots(figsize=(7,4)); ax.bar(summary.income_band.astype(str),summary['median'],color='#3478a5'); ax.set(xlabel='Income band (1 low to 5 high)',ylabel='₹ per month',title='Median willingness to pay'); ax.grid(axis='y',alpha=.2); st.pyplot(fig); plt.close(fig)
    with right:
        st.subheader('Interest and stated fee')
        fig,ax=plt.subplots(figsize=(7,4)); ax.scatter(view.interest,view.wtp_one_subject,alpha=.55,color='#e08b42'); ax.set(xlabel='Interest score (1–5)',ylabel='₹ per month',title='Each point is one synthetic response'); ax.grid(alpha=.2); st.pyplot(fig); plt.close(fig)
    st.subheader('Diagnostic checks')
    corr=view.select_dtypes(include='number').corr(numeric_only=True)
    focus=[c for c in ['wtp_one_subject','interest','current_spend','income_band','school_fee_tier','rote_concern'] if c in corr]
    st.dataframe(corr.loc[focus,focus].round(2),width='stretch')
    st.caption('Correlation is descriptive; it does not show that a factor causes fee willingness or enrolment.')

features=['child_class','num_children','school_fee_tier','income_band','parent_edu','both_working','english_home','current_spend','english_maths_spend','tuition_satisfaction','rote_concern','activity_belief','marks_focus','interest','max_distance_km','pref_batch_small']
features=[c for c in features if c in df.columns]
with tab2:
    st.subheader('Fee regression')
    reg=view[features+['wtp_one_subject']].dropna()
    if len(reg)>=30:
        X=reg[features]; y=reg.wtp_one_subject
        Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42)
        for name,model in [('Linear',LinearRegression()),('Ridge',RidgeCV(alphas=np.logspace(-2,3,30))),('Lasso',LassoCV(cv=5,random_state=42,max_iter=10000))]:
            pipe=make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),model); pipe.fit(Xtr,ytr); pred=pipe.predict(Xte)
            if name=='Linear': results=[]
            results.append([name,round(r2_score(yte,pred),3),round(mean_absolute_error(yte,pred),0),round(mean_squared_error(yte,pred)**.5,0)])
        st.dataframe(pd.DataFrame(results,columns=['Model','R²','MAE (₹)','RMSE (₹)']),hide_index=True,width='stretch')
        st.caption('Single 75/25 holdout for demonstration. Replace with real data and repeated cross-validation before decisions.')
    else: st.info('Need at least 30 complete rows for the demonstration regression.')
    st.subheader('Enrolment intent classification')
    cls=view[features+['high_enrol_intent']].dropna()
    if len(cls)>=40 and cls.high_enrol_intent.nunique()==2:
        X=cls[features]; y=cls.high_enrol_intent.astype(int)
        Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
        models={
          'Logistic regression':make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),LogisticRegression(max_iter=2000,class_weight='balanced')),
          'K-NN':make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),KNeighborsClassifier(n_neighbors=7,weights='distance')),
          'Decision tree':make_pipeline(SimpleImputer(strategy='median'),DecisionTreeClassifier(max_depth=4,class_weight='balanced',random_state=42)),
          'Random forest':make_pipeline(SimpleImputer(strategy='median'),RandomForestClassifier(n_estimators=300,class_weight='balanced',random_state=42,min_samples_leaf=3)),
          'Gradient boosting':make_pipeline(SimpleImputer(strategy='median'),GradientBoostingClassifier(random_state=42)),
          'SVM':make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),SVC(probability=True,class_weight='balanced',random_state=42)),
          'Naive Bayes':make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),GaussianNB())}
        rows=[]
        for name,model in models.items():
            model.fit(Xtr,ytr); pred=model.predict(Xte)
            try: auc=roc_auc_score(yte,model.predict_proba(Xte)[:,1])
            except Exception: auc=np.nan
            rows.append([name,accuracy_score(yte,pred),precision_score(yte,pred,zero_division=0),recall_score(yte,pred,zero_division=0),f1_score(yte,pred,zero_division=0),auc])
        st.dataframe(pd.DataFrame(rows,columns=['Model','Accuracy','Precision','Recall','F1','ROC-AUC']).round(3),hide_index=True,width='stretch')
        st.caption('Target = survey enrol_intent score 4–5. Metrics describe this synthetic holdout only and must not be used for offers or student decisions.')
    else: st.info('Need at least 40 rows and both intent classes.')
    st.warning('K-NN for student levels requires real student diagnostic scores and teacher-reviewed labels. Parent survey data is not placement data.')

with tab3:
    st.subheader('Exploratory K-Means segments')
    segcols=[c for c in ['income_band','current_spend','interest','activity_belief','rote_concern','max_distance_km'] if c in view]
    seg=view[segcols].dropna()
    if len(seg)>=15:
        Z=StandardScaler().fit_transform(seg)
        k=st.slider('Number of clusters',2,6,3)
        km=KMeans(n_clusters=k,n_init=20,random_state=42).fit(Z)
        st.metric('Silhouette score',f'{silhouette_score(Z,km.labels_):.2f}')
        result=seg.assign(cluster=km.labels_).groupby('cluster').agg(['count','median'])
        st.dataframe(result,width='stretch')
        st.caption('Cluster names are deliberately not inferred. Review the profiles and validate them on real local data.')
    st.subheader('Association rules from attribute co-occurrence')
    tmp=view.copy()
    tmp['income_group']=pd.cut(tmp.income_band,[0,2,3,5],labels=['lower_income','middle_income','higher_income'])
    tmp['high_interest']=np.where(tmp.interest>=4,'high_interest','lower_interest')
    tmp['high_rote_concern']=np.where(tmp.rote_concern>=4,'high_rote_concern','lower_rote_concern')
    items=[]
    for _,r in tmp.iterrows(): items.append({str(r[c]) for c in ['income_group','high_interest','high_rote_concern'] if pd.notna(r[c])})
    support=st.slider('Minimum item support',.05,.50,.12,.01); rules=[]
    single=Counter(i for row in items for i in row); n=len(items)
    pairs=Counter(tuple(sorted(p)) for row in items for p in __import__('itertools').combinations(sorted(row),2))
    for pair,count in pairs.items():
        sup=count/n; conf=count/max(single[pair[0]],1); lift=conf/(single[pair[1]]/n)
        if sup>=support: rules.append([pair[0],pair[1],round(sup,2),round(conf,2),round(lift,2)])
    st.dataframe(pd.DataFrame(rules,columns=['If','Then (co-occurs)','Support','Confidence','Lift']).sort_values('Lift',ascending=False) if rules else pd.DataFrame(columns=['If','Then (co-occurs)','Support','Confidence','Lift']),hide_index=True,width='stretch')
    st.caption('Pair rules are co-occurrences in synthetic responses. Lift above 1 is not evidence of causation.')

with tab4:
    st.subheader('Business diagnosis')
    st.markdown('''**Working as a testable concept**\n- A focused English and mathematics offer for Classes 1–8.\n- Skill-based beginner, intermediate, and advanced groups can be piloted with teacher-reviewed diagnostics.\n- Trial classes and real price tests can measure conversion.\n\n**Evidence gaps**\n- Sample data is synthetic; intent and fee figures are not market validation.\n- Locality and PIN code are blank, so site choice cannot be analysed.\n- No student assessment, attendance, retention, payment, cost, or learning-gain data exists.\n\n**Next step**\nCollect consented local survey data, run one small pilot, measure paid conversion and learning progress, then revisit models. Do not use this dashboard to place individual children.''')
st.caption('Prepared for an academic project. Replace the sample CSV with real, consented responses before business decisions.')
