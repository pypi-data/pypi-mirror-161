# 2022.6.9
from common import *
import random 

def run():
	st.header("Scoring data mocking")
	st.sidebar.write( "select") 
	rid = st.text_input('rid', app_state.get('tid',0))
	tid = st.text_input('tid', app_state.get('tid','scoring-0') )
	uids = st.sidebar.slider("total uids", 1, 50, 10)

	sleep = st.sidebar.slider("sleeping time", 0, 10, 0)
	loop = st.sidebar.slider("loop count", 0, 100, 20)
	reset = st.sidebar.checkbox('reset', True)
	if reset: [ redis.r.delete(k) for k in redis.r.keys(f"rid-{rid}:tid-{tid}:*")] # keep config
	
	if st.sidebar.button("submit"):
		for i in range(loop):
			uid = random.randint(0, uids - 1) 
			score = random.randint(0, 100) 
			redis.r.hset(f"rid-{rid}:tid-{tid}:uid-{uid}","score", score, {"rid": rid, "tid": tid,"uid": uid, "type":"scoring"} )
			st.metric("SCORE", score )
			if sleep: time.sleep( sleep) 

if __name__ == '__main__': run()