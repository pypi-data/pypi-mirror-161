# 2022.6.15
from common import *

mpublish = lambda mhost, ex, msg, routing_key='': requests.post(f"http://root:jkpigai!@{mhost}:15672/api/exchanges/%2f/{ex}/publish", json={"properties":{},"routing_key":routing_key,"payload":msg if isinstance(msg, str) else json.dumps(msg),"payload_encoding":"string"}).text

def run():
	st.sidebar.header("Penly resend")
	mhost = st.sidebar.text_input('mq host', 'ap.penly.cn')
	key = st.sidebar.selectbox( 'Which key to resend', redis.r.hkeys("config:resend"))
	
	if st.sidebar.button("submit"):
		st.sidebar.write(key) 
		for k in redis.r.zrange(key, 0, -1): 
			st.write(k) 
			mpublish(mhost, "pen", k, routing_key = 'resend')

if __name__ == '__main__': run()