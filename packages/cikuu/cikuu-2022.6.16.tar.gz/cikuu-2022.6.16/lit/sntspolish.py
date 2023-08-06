# 2022.6.8  sntspolish
from common import * 

def run():
	params = st.experimental_get_query_params() 
	params = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}

	rid = params.get('rid', 0)
	uid = params.get('uid', 0)

	tid = st.experimental_get_query_params().get('tid', ['sntspolish'])[0] 

	st.title(hget(f"config:rid-{rid}:tid-{tid}","title", "按句润色")) 
	st.caption(hget(f"config:rid-{rid}:tid-{tid}","subtitle")) 

	snts = json.loads(hget(f"config:rid-{rid}:tid-{tid}","snts", '[]')) 
	tgts = json.loads(hget(f"rid-{rid}:tid-{tid}:uid-{uid}","snts", '[]'))
	if not tgts : tgts = snts
	labels = [st.text_input( f"[{i+1}] {snt}",  tgts[i] ) for i, snt in enumerate(snts)]
	if st.button("submit", help=f"rid-{rid}:tid-{tid}:uid-{uid}") and tgts: 
		# if debug:  st.sidebar.write(tgts) 
		id = redis.r.xadd(xname, {"rid": rid, "tid": tid,"uid": uid, "essay_or_snts": json.dumps(labels), "submit": 1,"type":"sntspolish"})
		# if debug: st.sidebar.write( redis.r.xrevrange(xname, count=1))

		res = redis.r.blpop(f"xdsk:{id}", timeout=int(app_state.get('timeout',5)))
		# if debug: st.sidebar.write(res)  
		if res: st.metric("SCORE", round(float(json.loads(res[1]).get('info',{}).get("final_score",0)), 2) )

if __name__ == '__main__': run()