# 2022.6.8  fillmul (cross multiple words, ... )  # select trimBoth(arrayJoin (splitByChar (',', '123,456, 142354 ,23543') )) 
from common import * 
from collections import Counter 

def get_score(label, dic , max_score = 3): 
	''' 3,2,1 '''
	return sum([ abs(max_score - i) if w in dic else 0 for i,w in enumerate(label.strip().split(','))])

def run():
	params = st.experimental_get_query_params() 
	params = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}

	rid = params.get('rid', 0)
	uid = params.get('uid', 0)

	tid = st.experimental_get_query_params().get('tid', ['fillmul'])[0]


	st.title(hget(f"config:rid-{rid}:tid-{tid}","title", "好词好句")) 
	st.caption(hget(f"config:rid-{rid}:tid-{tid}","subtitle")) 
	topk = 3 

	label= st.text_input( f"Input comma-separated words:", hget(f"rid-{rid}:tid-{tid}:uid-{uid}", "label") )
	if st.button("submit"): 
		redis.r.hset(f"rid-{rid}:tid-{tid}:uid-{uid}", "label" , label, {"rid": rid, "tid": tid,"uid": uid, "type":"fillmul"} )
		[ redis.r.hset(f"rid-{rid}:tid-{tid}:uid-{uid}", f"label-{i}",  w.strip()) for i,w in enumerate(label.strip().split(',')) ]

		redis.r.hset(f"score:rid-{rid}:tid-{tid}:label", uid, label)  
		si = Counter()
		[ si.update({w.strip():1}) for label in redis.r.hvals(f"score:rid-{rid}:tid-{tid}:label") for w in label.strip().split(',')]
		refer = dict(si.most_common(topk))

		# re-score all uids 
		for uid in redis.r.keys(f"rid-{rid}:tid-{tid}:uid-*"):
			redis.r.hset(f"score:rid-{rid}:tid-{tid}", uid, get_score(label, refer) )
		scores = [ float(s) for s in redis.r.hvals(f"score:rid-{rid}:tid-{tid}")]
		if scores: redis.r.hset(f"score:rid-{rid}:tid-{tid}:avg", "avg", round(sum(scores)/ (len(scores)+0.00001),2), {"max": max(scores), "min": min(scores)} )

		st.metric("SCORE", hget(f"score:rid-{rid}:tid-{tid}", uid) )

if __name__ == '__main__': run()