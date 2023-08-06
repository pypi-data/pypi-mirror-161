# 2022.6.8 used by class i + 1 
import streamlit as st
import time,redis, requests ,json, platform

app_state = st.experimental_get_query_params() 
app_state = {k: v[0] if isinstance(v, list) else v for k, v in app_state.items()} 

rhost,rport,rdb		= app_state.get('rhost','127.0.0.1' if 'windows' in platform.system().lower() else '172.17.0.1') , app_state.get('rport',6379), app_state.get('rdb', 0)
xname				= app_state.get('xname','xdsk:rid-tid-uid') #xgecdsk
if not hasattr(redis, 'r'): redis.r	= redis.Redis(host=rhost, port=rport, db=rdb, decode_responses=True)

# 只有首次才加载 无效
# st.session_state['rid']		= app_state.get('rid',0)
# st.session_state['tid']		= app_state.get('tid',0)
# st.session_state['uid']		= app_state.get('uid','0') #+ "," +  app_state.get('uname','')

# rid,tid,uid		= st.session_state['rid'], st.session_state['tid'], st.session_state['uid']
# debug			= 'debug' in app_state or redis.r.hexists(f"config:rid-{rid}", "debug")

now		= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
hget	= lambda key, hkey, default='': ( res:=redis.r.hget(key, hkey), res if res else default )[-1]

#from streamlit_autorefresh import st_autorefresh
#st_autorefresh(interval=3000, key="fizzbuzzcounter") #limit=100,
# st.experimental_set_query_params( show_map=True,      selected=["asia", "america"], )  #https://docs.streamlit.io/library/api-reference/utilities/st.experimental_set_query_params