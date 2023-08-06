# 2022.7.26 pip install streamlit-aggrid pyecharts streamlit_echarts pandas numpy matplotlib seaborn
import time,redis, requests ,json, platform,os,re,builtins
from collections import Counter,defaultdict
import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import numpy as np 
import matplotlib
import seaborn as sns

st.set_page_config (layout="wide")
urlroot		= os.getenv('urlroot', 'http://cpu76.wrask.com:8000')  

@st.cache
def rows(sql): return requests.get(f"{urlroot}/kpsi/rows", params={'sql':sql}).json()
cplist		= [row[0].split('_')[0].strip() for row in rows("show tables") if row[0].endswith("_snt")] #['bnc', 'clec', 'dic', 'fengtai', 'gaokao', 'gblog', 'guten', 'gzjc', 'nju', 'nyt', 'qdu', 'sino', 'twit']
poslist		= ["VERB","NOUN","ADJ","ADV","LEX","LEM"]
rellist		= ["dobj:NOUN", "~dobj:VERB", "amod:ADJ", "~amod:NOUN"]
trplist		= ["VERB:dobj:NOUN, NOUN:~dobj:VERB, NOUN:amod:ADJ, ADJ:~amod:NOUN"]

rels = { 
"VERB": ["dobj:NOUN", "nsubj:NOUN", "advmod:ADV", "oprd:ADJ", "oprd:NOUN"],
"NOUN": ["~dobj:VERB", "~nsubj:VERB", "amod:ADJ"],
"ADJ": [ "~amod:NOUN"],
"ADV": ["~advmod:ADJ","~advmod:VERB"],
}

kn_sumkey = {
"#VERB": ["*:VERB:%", "VERB:%"],  #with src as ( select *, (select i from kpsi.clec where s = '#VERB') sumi from kpsi.clec where s like '*:VERB:%'), tgt as ( select *, (select i from kpsi.dic where s = '#VERB') sumi from kpsi.dic where s like '*:VERB:%') select tgt.s, src.i, src.sumi, tgt.i ti, tgt.sumi tsumi, keyness(src.i, tgt.i, src.sumi, tgt.sumi) kn from src right outer join tgt on src.s= tgt.s  order by kn 
"#NOUN": ["*:NOUN:%", "NOUN:%"],
"LEM:sound": ["sound:POS:%", "sound:LEX:%"],
"knowledge:NOUN:~dobj":  ["knowledge:NOUN:~dobj:VERB:%"], 
"open:VERB:dobj":  ["open:VERB:dobj:NOUN:%"], 
"consider:VERB": ["consider:VERB:be_vbn_p:%","consider:VERB:vtov:%","consider:VERB:VBN:%"],
}

@st.cache
def geti(cp,s):
	res = rows(f"select i from {cp} where s = '{s}' limit 1")
	return res[0][0] if res and len(res) > 0 else 0 

@st.cache
def slike(cp,pattern, topk:int=10):
	return rows(f"select substring_index(s,':',-1) ,i,snt from {cp},{cp}_snt where s like '{pattern}' and t = sid order by i desc limit {topk}")
#print ( slike("dic", "open:VERB:dobj:NOUN:%") )  #[['door', 255, 'A coachman has to drive, a groom has to open the door, a peon has to shout warnings.'], ['eye', 67, 'And even when revolution or military defeat should have opened eyes, distorted versions of reality survive.'], ['window', 66, "And then suddenly I pop back to life, clamber across Jenny's lap and open the window."], ['mouth', 62, "'I'll go,' Travis said quickly before she could open her mouth."], ['fire', 59, 'According to eyewitness accounts, soldiers opened fire on the crowd.'], ['account', 36, 'All you need to open the account is'], ['gate', 27, "And it's five, six, seven, open up the pearly gates."], ['store', 26, 'Argos opened 19 stores last year, with 25 more planned for 1993.'], ['letter', 23, 'A police spokesman said if the man had gone much further in opening the letter, he could have been killed.'], ['box', 22, 'After building your own machine you certainly will not be worried about opening the box!']]

@st.cache
def sisnt(cp="dic",pattern="open:VERB:dobj:NOUN:%", topk:int=10, color:str="#d65f5f"): #https://user-images.githubusercontent.com/27242399/140746511-1205f24a-869f-4b24-9ed7-9153cfeef8e3.png
	df = pd.DataFrame(slike(cp, pattern), columns=["Word", "Count", "Sentence"]).sort_values(by="Count", ascending=False).reset_index(drop=True)
	df.index += 1
	return df.style.bar(subset=['Count'], color=color) 	#st.table(df)

def add_style(df):
	cmGreen = sns.light_palette("green", as_cmap=True)
	cmRed = sns.light_palette("red", as_cmap=True)
	df = df.style.background_gradient(cmap=cmGreen,subset=["Relevancy",],)
	#df = df.format({"Relevancy": "{:.1%}",})
	return df

def attr(pos): 
	if not hasattr(attr, pos): setattr(attr, pos, [row[0] for row in rows(f"select substring_index(s,':',-1) w from bnc where s like '*:VERB:%' and i > 1000")])
	return getattr(attr, pos) 
#print ( attr('VERB'))# ['ROOT', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'Vend', 'acl', 'acomp', 'advcl', 'advmod', 'agent', 'amod', 'appos', 'attr', 'aux', 'auxpass', 'be_vbn_p', 'cc', 'ccomp', 'compound', 'conj', 'csubj', 'csubjpass', 'dative', 'dep', 'det', 'dobj', 'expl', 'intj', 'mark', 'meta', 'neg', 'nmod', 'npadvmod', 'nsubj', 'nsubjpass', 'nummod', 'oprd', 'parataxis', 'pcomp', 'pobj', 'poss', 'preconj', 'prep', 'prt', 'punct', 'relcl', 'sattr', 'sva', 'svc', 'svo', 'svx', 'vap', 'vdp', 'vnp', 'vnpn', 'vp', 'vpg', 'vpn', 'vpnpn', 'vppn', 'vprt', 'vtov', 'vvbg', 'xcomp', '~acl', '~acomp', '~advcl', '~advmod', '~amod', '~appos', '~attr', '~case', '~ccomp', '~compound', '~conj', '~csubj', '~csubjpass', '~dep', '~dobj', '~intj', '~nmod', '~npadvmod', '~nsubj', '~nsubjpass', '~oprd', '~parataxis', '~pcomp', '~pobj', '~prep', '~punct', '~relcl', '~xcomp']
 
@st.cache
def kndata(sumkey='knowledge:NOUN:~dobj', cps:str='clec', cpt:str='dic', slike:str="knowledge:NOUN:~dobj:VERB:%"): 
	''' return (word, srccnt, tgtcnt, srcsum, tgtsum, keyness) , 2022.7.24 '''
	return requests.get(f"{urlroot}/kpsi/kndata", params={"sumkey":sumkey, "cps":cps, "cpt":cpt, "slike":slike}).json()

mf		= lambda s='VERB:consider', cps='gzjc,clec,dic' :  rows(' union all '.join ( [f"select '{cp}' name, 1000000 * i / (select i from {cp} where s = '#SNT') mf from {cp} where s = '{s}'" for cp in cps.strip().split(',')]) )
trpsnts = lambda s,cp, topk: requests.get(f"{urlroot}/kpsi/snts", params={"s":s, "cp":cp, "topk":topk, "hl_words":f"{s.split(':')[0]},{s.split(':')[-1]}"}).text
def snts(cp, s, topk:int=10): 
	_sidlist= rows(f"select substring_index(t,',',{topk}) from {cp} where s = '{s}' limit 1")[0][0]
	word	= s.split(':')[-1]
	return [ re.sub(rf'\b{word}\b', f'<font color="red">{word}</font>', row[0]) for row in rows (f"select snt from {cp}_snt where sid in ({_sidlist}) ")  ]
#print (snts("clec", 'open:VERB:dobj:NOUN:door')) #st.write(f"{i+1}. {snt}", unsafe_allow_html=True)
#print (mf()) #[['gzjc', 2704.8349], ['clec', 3810.3077], ['dic', 3863.9423]]

@st.cache
def vecso_snthtml(snt, name, topk=10): 
	return  requests.get(f"{urlroot}/hnswlib", params={"snt":snt, "topk":topk, "name":name}).text #http://cpu76.wrask.com:8000/hnswlib?snt=I%20am%20too%20tired%20to%20move%20on.&topk=10&name=dic

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
def grid_gb(df, pagesize=10): 
	gb = GridOptionsBuilder.from_dataframe(df)
	#customize gridOptions  pip install streamlit-aggrid
	gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
	gb.configure_side_bar()
	gb.configure_selection("single")
	gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=pagesize)
	gb.configure_grid_options(domLayout='normal')
	return gb

def grid_response(df, height=400):
	gb = grid_gb(df) 
	return AgGrid(
		df, 
		gridOptions=gb.build(),
		height=height, 
		width='100%',
		data_return_mode=DataReturnMode.__members__["FILTERED"], 
		update_mode=GridUpdateMode.__members__["MODEL_CHANGED"],
		fit_columns_on_grid_load=True, # auto fit 
		allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
		)

def grid(tab, df, height=400, f = lambda row: None): # upgrade version of grid_response 
	with tab: 
		gb = grid_gb(df) 
		g = AgGrid(
			df, 
			gridOptions=gb.build(),
			height=height, 
			width='100%',
			data_return_mode=DataReturnMode.__members__["FILTERED"], 
			update_mode=GridUpdateMode.__members__["MODEL_CHANGED"],
			fit_columns_on_grid_load=True, # auto fit 
			allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
			)
		if g['selected_rows']: 
			row = g['selected_rows'][0] # dict , row['word']
			f(row) 

import altair as alt
from pyecharts import options as opts #https://share.streamlit.io/andfanilo/streamlit-echarts-demo/master/app.py
from pyecharts.charts import Bar
from streamlit_echarts import st_pyecharts, st_echarts

def single_bar(data, height:int=400):
	options = {
		"xAxis": {
			"type": "category",
			"data": [s for s,i in data  ],
		},
		"yAxis": {"type": "value"},
		"series": [{"data": [i for s,i in data ], "type": "bar"}],
	}
	events = {
		"click": "function(params) { return params.name }",
		#"dblclick": "function(params) { return [params.type, params.name, params.value] }",
	}

	#st.markdown("Click on a bar for label + value, **double** click to see type+name+value")
	s = st_echarts(options=options, events=events, height=f"{height}px") #, key="render_basic_bar_events"
	return s 

def pie(si, height:int=500):
	options = {
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "series": [
        {
            "name": "访问来源",
            "type": "pie",
            "radius": ["40%", "70%"],
            "avoidLabelOverlap": False,
            "itemStyle": {
                "borderRadius": 10,
                "borderColor": "#fff",
                "borderWidth": 2,
            },
            "label": {"show": False, "position": "center"},
            "emphasis": {"label": {"show": True, "fontSize": "40", "fontWeight": "bold"}},
            "labelLine": {"show": False},
            "data":   [ {"value":i, "name":s} for s,i in si ],
        }
    ],
}
	return st_echarts(options=options, height=f"{height}px",)

def bar_si(dic):
	b = (
    Bar()
    .add_xaxis([k for k,v in dic.items()]) 
    .add_yaxis(q, [v for k,v in dic.items()] )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="Collocation Frequency", subtitle="per million sentences"
        ),
        toolbox_opts=opts.ToolboxOpts(),
    )
)
	st_pyecharts(b)


def bar_data(data, y_label='Count', title=None, subtitle=None ):
	b = (
		Bar()
		.add_xaxis([s for s,i in data])
		.add_yaxis(y_label, [i for s,i in data])
		.set_global_opts(
			title_opts=opts.TitleOpts(
				title=title, subtitle=subtitle
			),
			toolbox_opts=opts.ToolboxOpts(),
		)
	)
	st_pyecharts(
		b, key="echarts"
	)  # Add key argument to not remount component at every Streamlit run

def bar_simple(): #https://share.streamlit.io/andfanilo/streamlit-echarts-demo/master/app.py
	options = {
    "xAxis": {
        "type": "category",
        "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
    "yAxis": {"type": "value"},
    "series": [{"data": [120, 200, 150, 80, 70, 110, 130], "type": "bar"}],
}
	st_echarts(options=options, height="500px")

def bar_dual(x=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], y1=[120, 200, 150, 80, 70, 110, 130], y2=[120, 200, 150, 80, 70, 110, 130]): 
	''' added 2022.7.22 '''
	options = { 
    "xAxis": {"type": "category","data": x,  },
    "yAxis": {"type": "value"},
    "series": [{"data": y1, "type": "bar"},{"data": y2, "type": "bar"}],}
	st_echarts(options=options, height="500px")


from math import log as ln
def likelihood(a,b,c,d, minus=None):  #from: http://ucrel.lancs.ac.uk/llwizard.html
	try:
		if a is None or a <= 0 : a = 0.000001
		if b is None or b <= 0 : b = 0.000001
		E1 = c * (a + b) / (c + d)
		E2 = d * (a + b) / (c + d)
		G2 = round(2 * ((a * ln(a / E1)) + (b * ln(b / E2))), 2)
		if minus or  (minus is None and a/c < b/d): G2 = 0 - G2
		return G2
	except Exception as e:
		print ("likelihood ex:",e, a,b,c,d)
		return 0

[setattr(builtins, k, v) for k, v in globals().items()] 

if __name__ == '__main__': 
	pass 