# 2022.6.21
from common import *

def run():
	params = st.experimental_get_query_params() 
	params = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}

	rid = params.get('rid', 0)
	uid = params.get('uid', 0)

	tid = st.experimental_get_query_params().get('tid', ['single'])[0]
	st.caption(hget(f"config:rid-{rid}:tid-{tid}","subtitle")) 
	# if  debug: st.sidebar.write(f"info = rid:{rid}, tid:{tid}, uid:{uid}")

	st.title(hget(f"config:rid-{rid}:tid-{tid}","title", "[单选]") + " " + hget(f"config:rid-{rid}:tid-{tid}","body"))
	arr = json.loads(hget(f"config:rid-{rid}:tid-{tid}","cands","{}")) # take : A 
	item   = st.radio('',[ f"{v}. {k}" for k,v in arr.items()], index={"A":0, "B":1, "C":2, "D":3}.get(hget(f"rid-{rid}:tid-{tid}:uid-{uid}","label"), 0))
	if st.button("submit") : 
		redis.r.hset(f"rid-{rid}:tid-{tid}:uid-{uid}","label", item.split('.')[0], {"rid": rid, "tid": tid,"uid": uid, "type":"single"} )
		score = 1 if item.split('.')[0] == hget(f"config:rid-{rid}:tid-{tid}","key") else 0
		st.metric("SCORE", score )

if __name__ == '__main__': run()