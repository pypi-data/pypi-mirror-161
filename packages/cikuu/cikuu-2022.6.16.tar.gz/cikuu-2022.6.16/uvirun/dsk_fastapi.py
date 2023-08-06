# 2022.6.30 cp from dsk/__init__.py , NO redis 
from uvirun import * 
import json, requests,time,sys, traceback, difflib,os, en

trans_diff		= lambda src, trg:  [] if src == trg else [s for s in difflib.ndiff(src, trg) if not s.startswith('?')] #src:list, trg:list
trans_diff_merge= lambda src, trg:  [] if src == trg else [s.strip() for s in "^".join([s for s in difflib.ndiff(src, trg) if not s.startswith('?')]).replace("^+","|+").split("^") if not s.startswith("+") ]
def mkf_input(snts, docs, tokenizer, sntdic:dict={},diffmerge:bool=False): 
	''' mkf input for 7095 java calling '''
	srcs	= [ [t.text for t in doc] for doc in docs]
	tgts	= [ [t.text for t in doc] if ( snt not in sntdic or snt == sntdic.get(snt,snt) ) else [t.text for t in tokenizer(sntdic.get(snt,snt))] for snt, doc in zip(snts, docs)]
	input	= [ {"pid":0, "sid":i, "snt":snts[i], "tok": [t.text for t in doc],  
				"pos":[t.tag_ for t in doc], "dep": [t.dep_ for t in doc],"head":[t.head.i for t in doc],  
				"seg":[ ("NP", sp.start, sp.end) for sp in doc.noun_chunks] + [ (np.label_, np.start,np.end) for np in doc.ents] , 
				"gec": sntdic.get(snts[i],snts[i]), "diff": trans_diff_merge( srcs[i] , tgts[i]) if diffmerge else  trans_diff( srcs[i] , tgts[i] )	}
				for i, doc in enumerate(docs)]
	return input #mkfs	= requests.post(f"http://172.17.0.1:7095/parser", data={"q":json.dumps(input).encode("utf-8")}).json()

# gec_redis=192.168.201.120:6379 uvicorn dsk_fastapi:app --host 0.0.0.0 --port 8080  
gec_redis = os.getenv('gec_redis','192.168.201.120:6379') # xsnts consumer deployed 
dsk_host  = os.getenv('dsk_host','172.17.0.1:7095')
@app.get('/dsk/xgec', tags=["dsk"])
def dsk_xgec(essay_or_snts:str="She has ready. It are ok.", asdsk:bool=True, timeout:int=5,): # rgec_host:str='192.168.201.120', rgec_port:int=6379 , dskhost:str='172.17.0.1:7095'
	''' assure: rgec_host is in the white ip list, added 2022.7.19 '''
	import redis
	if not hasattr(dsk_xgec,'r'): dsk_xgec.r = redis.Redis(host=gec_redis.split(":")[0], port=int(gec_redis.split(":")[-1]), decode_responses=True)
	tims	= [time.time()]
	snts	= json.loads(essay_or_snts) if essay_or_snts.startswith('["') else sntbr(essay_or_snts)
	id	= dsk_xgec.r.xadd("xsnts", {'snts':json.dumps(snts)})
	res = dsk_xgec.r.blpop([f"suc:{id}",f"err:{id}"], timeout=timeout)
	dsk_xgec.r.xdel("xsnts", id)
	tims.append(time.time())
	if res is None: return {"** failed xgec": essay_or_snts}

	sntdic = json.loads(res[1])
	docs	= [spacy.nlp(snt) for snt in snts ] 
	tims.append(time.time())
	input	= mkf_input(snts, docs, spacy.nlp.tokenizer, sntdic)
	dsk		= requests.post(f"http://{dsk_host}/parser", data={"q":json.dumps({"snts":input, "rid":"10"} if asdsk else input).encode("utf-8")}).json()
	tims.append(time.time())
	dsk['tim'] = {'gec': tims[1] - tims[0] , 'parse': tims[2] - tims[1] , 'mkf': tims[3] - tims[2] }
	return dsk

@app.get('/dsk/register_redis', tags=["dsk"])
def register_redis(rinfo:str='172.17.0.1:6379:0'):
	''' to enable redis cache for snt parsing , 2022.6.30 '''
	en.redis_xsntbytes = en.register_redis(rinfo, force=True)
	return en.redis_xsntbytes

@app.post('/dsk', tags=["dsk"])
def post_dsk(arr:dict={'essay_or_snts':"She has ready. It are ok.", # arr from mq 
				'formula':{ 
				"ast":[9.9, 11.99, 15.3, 18.51, 25.32,				2,0.0882, 0.3241],
				"awl":[3.5, 4.1, 4.56, 5.1, 6.0,					3,0.0882, 0.5],
				"b3":[0, 0.03, 0.08, 0.12, 0.15 ,					1, 0.0956, 0.2096],
				"cl_sum":[1, 6.68, 12, 16, 26,						2,0.0441, 0.1621],
				"grammar_correct_ri":[0.6, 0.85, 0.92, 0.97,1.0,	2,0.0368, 0.1352],
				"internal_sim":[0.0, 0.08, 0.2, 0.3, 0.4,			4, 0.0735, 0.7688],
				"kp_correct_ri":[0.7, 0.9, 0.95, 0.97, 1,			1, 0.0368, 0.0807],
				"mwe_pv":[0.01,8.03, 12, 20.21, 25,					4, 0.0221, 0.2312],
				"pred_diff_max3":[3.84, 5.11, 6.51, 7.9, 10.09 ,	1, 0.0368, 0.0807],
				"prmods_ratio":[0.06, 0.21, 0.3, 0.4, 0.5,			2, 0.0294, 0.108],
				"prmods_tc":[1.1, 2.76, 4.75, 6.76, 10.0,			2, 0.0368, 0.1352],
				"simple_sent_ri":[0.4, 0.65, 0.9, 0.95, 1,			2, 0.0368, 0.1352],
				"snt_correct_ratio":[0.01, 0.2, 0.45, 0.75, 1,		1, 0.0368, 0.0807],
				"spell_correct_ratio":[0.8, 0.9, 0.97, 0.99, 1,		1, 0.1471, 0.3226],
				"ttr1":[3.43, 4.28, 5.2, 6, 6.8,					3, 0.0882, 0.5],
				"word_diff_avg":[4.47, 4.73, 5.25,5.8, 6.6,			1, 0.0441, 0.0967],
				"word_gt7":[0.11, 0.19, 0.3, 0.42, 0.49,			1, 0.0588, 0.1289]}}
		, asdsk:bool=True, debug:bool= False, dskhost:str='172.17.0.1:7095'): 
	''' essay_or_snts:  either essay or snts, dumped by json.dumps, ' '''
	from dsk import score 
	from gec_fastapi import gecsnts
	try:
		tims	= [ ("start", time.time(), 0)] # tag, tm, delta 
		essay_or_snts = arr.get("essay_or_snts","")
		snts	= json.loads(essay_or_snts) if essay_or_snts.startswith('["') else en.sntbr(essay_or_snts)
		if hasattr(en,'redis_xsntbytes'): en.publish_newsnts(snts) 

		sntdic	= gecsnts(snts) # # localversion, return {'She has ready.': 'She is ready.', 'It are ok.': 'It is ok.'}
		if debug : tims.append( ("gec", time.time(), round(time.time() - tims[-1][1],2))  )
		docs	= [ en.parse_if(snt) if hasattr(en,'redis_xsntbytes') else spacy.nlp(snt) for snt in snts ] 
		if debug : tims.append( ("nlp", time.time(), round(time.time() - tims[-1][1],2))  )
		input	= mkf_input(snts, docs, spacy.nlp.tokenizer, sntdic)
		res		= requests.post(f"http://{dskhost}/parser", data={"q":json.dumps({"snts":input, "rid":"10"} if asdsk else input).encode("utf-8")}).json()
		if debug : tims.append( ("dsk", time.time(), round(time.time() - tims[-1][1], 2))  )
		if isinstance(res, dict) and 'info' in res:
			if debug  : res['info']['tim'] = tims #[('start', 1653811771.030599, 0), ('gec', 1653811776.2294545, 5.2), ('nlp', 1653811776.2439919, 0.01), ('dsk', 1653811776.275237, 0.03)]
			if 'formula' in arr : res['info'].update(  score.dims_score(res['doc'], arr['formula'])) # reset the score 
		return res  #docker run -d --restart=always --name dsk17095 -v /data/dct:/dct -p 7095:7095 wrask/gec:dsk8 java -Xmx4096m -jar pigai_engine8.jar --database-no-encrypt --server-addr dsk.wrask.com --server-port 7095  --database-type sqlite --sqlite-file dct/sqlite/pigai_spss.sqlite3 --thread-num 2 --gec-snts-address http://wrask.com:33000/gec/essay_or_snts
	except Exception as ex: 
		print(">>todsk Ex:", ex, "\t|", arr )
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)

@app.get('/dsk', tags=["dsk"])
def get_dsk(essay:str="She has ready. It are ok.", asdsk:bool=True, debug:bool= False, dskhost:str='172.17.0.1:7095'):
	''' '''
	return post_dsk({"essay_or_snts":essay}, asdsk, debug, dskhost)

@app.get('/dsk/wrapper', tags=["dsk"])
def dsk_wrapper(essay_or_snts:str="She has ready. It are ok.", asdsk:bool=True, timeout:int=5, gechost:str='gpu120.wrask.com:8180' , dskhost:str='gpu120.wrask.com:7095', JSONEachRow:bool=False): 
	''' simple wrapper for debug only, 2022.6.5 '''
	snts	= json.loads(essay_or_snts) if essay_or_snts.startswith('["') else sntbr(essay_or_snts)
	sntdic	= requests.post(f"http://{gechost}/getgecs", params={"timeout":timeout}, json=snts).json ()
	docs	= [spacy.nlp(snt) for snt in snts ] 
	input	= mkf_input(snts, docs, spacy.nlp.tokenizer, sntdic)
	dsk		= requests.post(f"http://{dskhost}/parser", data={"q":json.dumps({"snts":input, "rid":"10"} if asdsk else input).encode("utf-8")}).json()
	if JSONEachRow:  # added 2022.7.7
		for snt in dsk.get('snt', []):
			snt['feedback'] = [ v for k,v in snt.get('feedback',{}).items()]
	return dsk 

@app.get('/dsk/fds', tags=["dsk"])
def dsk_fds(essay_or_snts:str="She has ready. It are ok.", timeout:int=5, gechost:str='gpu120.wrask.com:8180' , dskhost:str='gpu120.wrask.com:7095'): 
	''' mkf JSONEachRow '''
	snts	= json.loads(essay_or_snts) if essay_or_snts.startswith('["') else sntbr(essay_or_snts)
	sntdic	= requests.post(f"http://{gechost}/getgecs", params={"timeout":timeout}, json=snts).json ()
	docs	= [spacy.nlp(snt) for snt in snts ] 
	input	= mkf_input(snts, docs, spacy.nlp.tokenizer, sntdic)
	mkfs	= requests.post(f"http://{dskhost}/parser", data={"q":json.dumps(input).encode("utf-8")}).json()

	def _getfd(mkf): 	
		res = 	{"snt": mkf.get('meta',{}).get('snt','')}
		for k,v in mkf.get('feedback',{}).items(): 
			res.update( {"cate": v.get('cate',''), "short_msg": v.get('short_msg','') } )
		return res

	return [ _getfd(ar) for ar in mkfs  ]

@app.get('/dsk/mkf', tags=["dsk"])
def dsk_mkf(essay_or_snts:str="She has ready. It are ok.", timeout:int=5, gechost:str='gpu120.wrask.com:8180' , dskhost:str='gpu120.wrask.com:7095'): 
	return dsk_wrapper(essay_or_snts, asdsk=False, timeout=timeout, gechost=gechost, dskhost=dskhost)

if __name__ == '__main__': #uvicorn.run(app, host='0.0.0.0', port=80)
	print ( dsk_fds()) 
	#print (dsk_wrapper("[\u8bd1\u6587]The 55-kilometre Hong Kong Zhuhai-Macau Bridge is an extraordinary engineering. It is the world's longest sea-crossing transportation system combining bridges and tunnels, which joins the three cities of Hong Kong Zhuhai and Macao, cutting the travelling time among them from 3 hours to 30 minutes. The reinforced concrete bridge with huge spans fully not only proves that China has the ability to complete the record-breaking mega-construction, but also will enhance the regional integration and boost the economic growth. It plays a crucial role in the overall plan to develop China’s Great Bay Area, which China intends to turn into one rivaling those of San Francisco, New York and Tokyo in terms of technological innovation and economic prosperity.", JSONEachRow=True))
	#print (sntbr("[\u8bd1\u6587]The 55-kilometre Hong Kong Zhuhai-Macau Bridge is an extraordinary engineering. It is the world's longest sea-crossing transportation system combining bridges and tunnels, which joins the three cities of Hong Kong Zhuhai and Macao, cutting the travelling time among them from 3 hours to 30 minutes. The reinforced concrete bridge with huge spans fully not only proves that China has the ability to complete the record-breaking mega-construction, but also will enhance the regional integration and boost the economic growth. It plays a crucial role in the overall plan to develop China’s Great Bay Area, which China intends to turn into one rivaling those of San Francisco, New York and Tokyo in terms of technological innovation and economic prosperity."))

def sntbr(essay, trim:bool=False, with_pid:bool=False): 
	''' sntbr("[\u8bd1\u6587]The 55-kilometre Hong Kong Zhuhai-Macau Bridge is an extraordinary engineering. It is the world's longest sea-crossing transportation system combining bridges and tunnels, which joins the three cities of Hong Kong Zhuhai and Macao, cutting the travelling time among them from 3 hours to 30 minutes. The reinforced concrete bridge with huge spans fully not only proves that China has the ability to complete the record-breaking mega-construction, but also will enhance the regional integration and boost the economic growth. It plays a crucial role in the overall plan to develop China’s Great Bay Area, which China intends to turn into one rivaling those of San Francisco, New York and Tokyo in terms of technological innovation and economic prosperity.") '''
	from spacy.lang import en
	if not hasattr(sntbr, 'inst'): 
		sntbr.inst = en.English()
		sntbr.inst.add_pipe("sentencizer")

	doc = sntbr.inst(essay)
	if not with_pid: return [ snt.text.strip() if trim else snt.text for snt in  doc.sents]
	pid = 0 #spacy.sntpidoff	= lambda essay: (pid:=0, doc:=spacy.sntbr(essay), [ ( pid := pid + 1 if "\n" in snt.text else pid,  (snt.text, pid, doc[snt.start].idx))[-1] for snt in  doc.sents] )[-1]
	arr = []
	for snt in  doc.sents:
		if "\n" in snt.text: pid = pid + 1 
		arr.append( (snt.text, pid) ) 
	return arr 

def topk_info(snts, docs,  topk, default_dims = {"internal_sim":0.2} ): 
	''' info computing with topk snts, upon those long essay '''
	from dsk import score, pingyu
	from en.dims import docs_to_dims
	
	info = {}
	dims = docs_to_dims(snts[0:topk], docs[0:topk]) # only top [0:topk] snts are considered for scoring 
	for k,v in default_dims: 
		if not k in dims: 
			dims[k] = v # needed by formular 

	info.update(score.dims_score(dims))
	info['pingyu'] = pingyu.get_pingyu(dims)
	info['dims']   = dims  # new dsk format , /doc -> /info/dims 
	return info 