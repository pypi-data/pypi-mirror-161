# 2022.6.8
from common import *

def run():
	tid = st.experimental_get_query_params().get('tid', ['essay'])[0]
	st.title(hget(f"config:rid-{rid}:tid-{tid}","title", "Essay Input")) 
	st.caption(hget(f"config:rid-{rid}:tid-{tid}","subtitle")) 

	essay = st.text_area( "Input an essay", hget(f"config:rid-{rid}:tid-{tid}",  "input-default"), height=350)
	if st.button("submit") : 
		st.session_state[f'rid-{rid}:tid-{tid}:uid-{uid}:essay'] = essay 
		id = redis.r.xadd(xname, {"rid": rid, "tid": tid,"uid": uid, "essay_or_snts": essay, "submit": 1})
		if 'debug' in app_state: st.sidebar.write( redis.r.xrevrange(xname, count=1))
		res = redis.r.blpop(f"xdsk:{id}", timeout=app_state.get('timeout',5))
		if 'debug' in app_state: st.sidebar.write(res)  
		if res: st.metric("SCORE", round(float(json.loads(res[1]).get('info',{}).get("final_score",0)), 2) )

if __name__ == '__main__': run()

