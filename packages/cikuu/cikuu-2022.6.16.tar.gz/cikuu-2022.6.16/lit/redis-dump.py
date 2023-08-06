# 2022.6.15
import streamlit as st
import pandas as pd
import time,redis, json

def dumpdf(r, pattern="*"):
	''' dump to db-0.ktv, (key, type, value) '''
	arr = [] 
	for k in r.keys(pattern): 
		try:
			type =  r.type(k)
			v = r.hgetall(k) if type == 'hash' else  dict(r.zrevrange(k, 0,-1, True) ) if type == 'zset' else r.lrange(k, 0,-1) if type =='list' else r.smembers(k) if type =='set' else r.get(k) if type == 'string' else ''
			if v: arr.append({"key":k, "type":type, "v": v if type =='string' else json.dumps(v)}) # skip other type 
		except Exception as e: 
			print ( "ex:" , e, k ) 
	return pd.DataFrame.from_dict(arr)

def run():
	st.sidebar.header("redis dump")
	host = st.sidebar.text_input('redis host', '172.17.0.1')
	port = st.sidebar.text_input('redis port', 6379)
	db = st.sidebar.text_input('redis db', 0)
	pattern = st.sidebar.text_input('pattern', 'config:*')
	r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
	
	st.sidebar.download_button(label="Download data as df CSV",	 data=dumpdf(r, pattern).to_csv().encode('utf-8'), mime='text/csv',	 ) #file_name='large_df.csv',
	if st.sidebar.button("del keys"): st.write([r.delete(k) for k in r.keys(pattern)])

	uploaded_file = st.file_uploader("Choose a df-dumped file to upload")
	if uploaded_file is not None: 		# Can be used wherever a "file-like" object is accepted:
		df = pd.read_csv(uploaded_file)
		st.write(df)
		for ind in df.index:
			k,type,v = df['key'][ind], df['type'][ind], df['v'][ind]
			if type == 'hash':  r.hmset(k, json.loads(v))
			elif type == 'zset': r.zadd(k, json.loads(v))
			elif type == 'list': [r.rpush(k, s) for s in json.loads(v)]
			elif type == 'set': [r.sadd(k, s) for s in json.loads(v)]
			elif type == 'string': 	r.set(k, v) 

if __name__ == '__main__': run()