# 2022.6.16
import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(layout='wide')
from common import * 

params = st.experimental_get_query_params() 
params = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}

rid = params.get('rid', 0)
uid = params.get('uid', 0)

st.sidebar.header( hget(f"config:rid-{rid}", "title","i+1 写作智慧课堂") + f"[{rid}]" )
st.sidebar.caption(uid.split(',')[-1])

keys = redis.r.keys(f'config:rid-{rid}:teacher:*') 
item = st.sidebar.radio('', [k.split(':')[-1] for k in keys]) 

st.sidebar.markdown('''---''') 
url  = hget(f'config:rid-{rid}:teacher:{item}', 'url')
tags = { k : st.sidebar.radio(hget('config:plusone:settings',k,k),  json.loads(hget(f'config:rid-{rid}:teacher:{item}', k)) ) for k in redis.r.hkeys(f'config:rid-{rid}:teacher:{item}') if k.startswith('var-')}
if tags:
	for k,v in tags.items(): # {var-sid: 4}
		url = url.replace(f"${k}", str(v)) 
components.iframe( url ,  height = 1200) #width=1500,