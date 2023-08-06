# 2022.6.8
from common import *

def run():
	tid = st.experimental_get_query_params().get('tid', ['filling'])[0]
	st.title(hget(f"config:rid-{rid}:tid-{tid}","title", "Filling")) 
	st.caption(hget(f"config:rid-{rid}:tid-{tid}","subtitle")) 

	label = st.text_input('Input:', '')
	if st.button("submit") : 
		redis.r.hset(f"rid-{rid}:tid-{tid}:uid-{uid}","label", label, {"rid": rid, "tid": tid,"uid": uid, "type":"filling"} )
		#st.metric("SCORE", score )

if __name__ == '__main__': run()

