# 2022.6.17
from common import *

def run():
	params = st.experimental_get_query_params() 
	params = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}

	rid = params.get('rid', 0)
	uid = params.get('uid', 0)
	tid = st.experimental_get_query_params().get('tid', ['scoring-0'])[0]

	st.title(hget(f"config:rid-{rid}:tid-{tid}","title", "Scoring")) 
	st.caption(hget(f"config:rid-{rid}:tid-{tid}","subtitle")) 

	score = st.number_input('Input a score', min_value=0, max_value=100,step=1, value=int(hget(f"rid-{rid}:tid-{tid}:uid-{uid}","score", 60)))
	if st.button("submit") : 
		redis.r.hset(f"rid-{rid}:tid-{tid}:uid-{uid}","score", score, {"rid": rid, "tid": tid,"uid": uid, "type":"scoring"} )
		st.metric("SCORE", score )

		# to be removed when can get in grafana, to compute Max/Min
		redis.r.hset(f"score:rid-{rid}:tid-{tid}", uid, score)  
		scores = [ float(s) for s in redis.r.hvals(f"score:rid-{rid}:tid-{tid}")]
		if scores: redis.r.hset(f"score:rid-{rid}:tid-{tid}:avg", "avg", round(sum(scores)/ (len(scores)+0.00001),2), {"max": max(scores), "min": min(scores)} )

if __name__ == '__main__': run()