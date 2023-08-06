# 2022.6.8  reorder 
from common import * 

def run():
	params = st.experimental_get_query_params() 
	params = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}

	rid = params.get('rid', 0)
	uid = params.get('uid', 0)
	tid	= st.experimental_get_query_params().get('tid', ['reorder'])[0] 

	st.title(hget(f"config:rid-{rid}:tid-{tid}","title", "连词成句")) 
	st.caption(hget(f"config:rid-{rid}:tid-{tid}","subtitle")) 

	snts = json.loads(hget(f"config:rid-{rid}:tid-{tid}","snts", "[]")) 
	tgts = json.loads(hget(f"rid-{rid}:tid-{tid}:uid-{uid}","snts",'[]'))
	if not tgts : tgts = [''] * len(snts) 
	refers = json.loads( hget(f"config:rid-{rid}:tid-{tid}","refers", "[]" ))
	if not refers : refer = [''] * len(snts) 

	for i, snt in enumerate(snts): 
		tgts[i] = st.text_input( f"[{i+1}] {snt}", tgts[i]).strip()

	if st.button("submit", help=f"rid-{rid}:tid-{tid}:uid-{uid}") : 
		score = round(100 * len([snt for snt, refer in zip(tgts, refers) if snt == refer]) / len(snts), 2)
		redis.r.hset(f"rid-{rid}:tid-{tid}:uid-{uid}","snts", json.dumps(tgts), {"rid": rid, "tid": tid,"uid": uid, "type":"reorder"
				, "scores": json.dumps([ 1 if snt == refer else 0 for snt, refer in zip(tgts, refers)]), 'score':score} )
		redis.r.hset(f"score:rid-{rid}:tid-{tid}", f"rid-{rid}:tid-{tid}:uid-{uid}", score) # verbose, for counting convenience
		redis.r.xadd(f"xlog:rid-{rid}:tid-{tid}", {'uid':uid, 'tm':time.time(), 'score':score} ) # added 2022.6.13
		st.metric("SCORE", score )

if __name__ == '__main__': run()