# 2022.6.8
import streamlit as st
st.set_page_config(layout='wide')
from common import * 

params = st.experimental_get_query_params() 
params = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}

rid = params.get('rid', 0)
uid = params.get('uid', 0)

st.sidebar.header( hget(f"config:rid-{rid}", "title", f"i+1 写作智慧课堂") + f"[{rid}]" )
st.sidebar.caption(uid.split(',')[-1])  

radios = json.loads(hget(f"config:rid-{rid}","radios","{}"))
item   = st.sidebar.radio('',[k for k in radios.keys()], index= 0) # {"连词成句":"reorder", "句式升级":"essay", "按句润色":"sntspolish"}
st.sidebar.markdown('''---''') 

x = __import__(radios[item].split('-')[0], fromlist=['run'])
x.run()

#tids   = [k for k in radios.values()]
#index  = 0 if not 'tid' in st.experimental_get_query_params() else  tids.index(st.experimental_get_query_params()['tid'][0])
#st.experimental_set_query_params(rid=rid, tid=radios[item], uid=uid, uname=uname ) #app_state['tid'] = radios[item]