# 2022.7.2 cp from es_fastapi.py 
from uvirun import *

requests.eshp	= os.getenv("eshp", "es.corpusly.com:9200") # host & port 
#sqlcount		= lambda query: requests.post(f"http://{requests.eshp}/_sql",json={"query": query}).json()['rows'][0][0]

@app.get('/es/rows', tags=["es"])
def rows(query="select lem, count(*) cnt  from gzjc where type = 'tok' and pos != 'PUNCT' group by lem order by cnt desc limit 10", raw:bool=False
	, sum_query:str=None, add_cp:bool=False , eshost:str="es.corpusly.com:9200"):
	''' # select snt from dic where type = 'snt' and kp = 'book_VERB' limit 2 
	# sum_query: select count(*) from gzjc where type='snt' '''
	res = requests.post(f"http://{eshost}/_sql",json={"query": query}).json() 
	if raw: return res['rows']  
	si = [  dict(zip([ ar['name'] for ar in res['columns'] ] , ar)) for ar in res.get('rows',[]) ]  #[{"lem": "the", "cnt": 7552},{"lem": "be","cnt": 5640},
	if sum_query is not None: 
		sumi = requests.post(f"http://{eshost}/_sql",json={"query": sum_query}).json()['rows'][0][0]
		[row.update({"sumi":sumi}) for row in si] #return [  dict( dict(zip([ ar['name'] for ar in res['columns'] ] , ar)), **{"sumi":sumi}) for ar in res.get('rows',[]) ] 
	if add_cp: 
		cp = query.split("where")[0].split("from")[-1].strip()
		[row.update({"cp":cp}) for row in si]
	return si #return [  dict(zip([ ar['name'] for ar in res['columns'] ] , ar)) for ar in res.get('rows',[]) ] 

@app.get('/es/count', tags=["es"])
def rows_count(cp:str='gzjc', type:str='snt', eshost:str="es.corpusly.com:9200"):
	return [ {"cnt": requests.post(f"http://{eshost}/_sql",json={"query": f"select count(*) from {cp} where type = '{type}'"}).json()['rows'][0][0]} ]   

@app.get('/es/sum/{cps}/{type}', tags=["es"])
def es_sum(cps:str='gzjc,clec', type:str="snt", eshost:str="es.corpusly.com:9200"):
	'''  cps: gzjc,clec   type:snt   
	# [{'cp':'gzjc', 'snt': 8873}, {'cp':'clec', 'snt': 75322}] '''
	return [{"cp": cp, type: requests.post(f"http://{eshost}/_sql",json={"query": f"select count(*) from {cp} where type ='{type}'"}).json()['rows'][0][0]} for cp in cps.strip().split(',')]

@app.get("/es/kwic", tags=["es"])
def corpus_kwic(cp:str='dic', w:str="opened", eshost:str="es.corpusly.com:9200", topk:int=10, left_tag:str="<b>", right_tag:str="</b>"): 
	''' search snt using word,  | select snt,postag, tc from gzjc where type = 'snt' and match(snt, 'books') | 2022.6.19 '''
	return [] if topk <= 0 else [ {"snt": re.sub(rf"\b({w})\b", f"{left_tag}{w}{right_tag}", snt), "tc": tc } for snt, postag, tc in rows(f"select snt, postag, tc from {cp.strip().split(',')[0]} where type = 'snt' and match (snt, '{w}') limit {topk}", raw=True)]

@app.get('/es/outer_join', tags=["es"])
def es_outer_join(cps:str="clec,gzjc", query:str="select gov, count(*) cnt from clec where type = 'tok' and lem='door' and pos='NOUN' and dep='dobj' group by gov",  ): #perc:bool=False
	''' [{'cp0_1': 1.0, 'cp1_1': 0.0, 'word': 'clean_VERB'}, {'cp0_1': 11.0, 'cp1_1': 1.0, 'word': 'close_VERB'}, {'cp0_1': 2.0, 'cp1_1': 0.0, 'word': 'enter_VERB'}, {'cp0_1': 3.0, 'cp1_1': 0.0, 'word': 'have_VERB'}, {'cp0_1': 1.0, 'cp1_1': 0.0, 'word': 'keep_VERB'}, {'cp0_1': 3.0, 'cp1_1': 0.0, 'word': 'knock_VERB'}, {'cp0_1': 1.0, 'cp1_1': 0.0, 'word': 'lock_VERB'}, {'cp0_1': 31.0, 'cp1_1': 1.0, 'word': 'open_VERB'}, {'cp0_1': 1.0, 'cp1_1': 0.0, 'word': 'pull_VERB'}, {'cp0_1': 1.0, 'cp1_1': 0.0, 'word': 'push_VERB'}, {'cp0_1': 3.0, 'cp1_1': 0.0, 'word': 'reach_VERB'}, {'cp0_1': 1.0, 'cp1_1': 0.0, 'word': 'rush_VERB'}, {'cp0_1': 1.0, 'cp1_1': 1.0, 'word': 'shut_VERB'}, {'cp0_1': 1.0, 'cp1_1': 0.0, 'word': 'slam_VERB'}, {'cp0_1': 1.0, 'cp1_1': 0.0, 'word': 'unlock_VERB'}, {'cp0_1': 2.0, 'cp1_1': 0.0, 'word': 'watch_VERB'}, {'cp0_1': 0.0, 'cp1_1': 1.0, 'word': 'find_VERB'}, {'cp0_1': 0.0, 'cp1_1': 1.0, 'word': 'leave_VERB'}] '''
	cps = cps.strip().split(',')
	map = defaultdict(dict)
	for i, cp in enumerate(cps): 
		for row in rows(query.replace(cps[0], cp ) , raw=True): # assume the first one is the key 
			for j in range(1, len(row)): 
				map[ row[0]][ f"cp{i}_{j}"] = row[j]
	df = pd.DataFrame(map).fillna(0).transpose()
	return [ dict(dict(row), **{"word": index} ) for index, row in df.iterrows()]  #return arr[0:topk] if topk > 0  else arr 

@app.get("/es/stats", tags=["es"])
def corpus_stats(names:str=None, types:str="doc,snt,np,tok,trp,vp", eshost:str="es.corpusly.com:9200"):
	''' doc,snt,np,tok,simple_sent,vtov,vvbg,vp, added 2022.5.21 '''
	names = name.strip().split(',') if names else [ar['name'] for ar in sqlrows("show tables")  if not ar['name'].startswith(".") and ar['type'] == 'TABLE' and ar['kind'] == 'INDEX']
	types = types.replace(",", "','")
	return [ dict( dict(rows(f"select type, count(*) cnt from {name} where type in ('{types}') group by type")), **{"name":name} ) for name in names]

@app.get("/es/phrase", tags=["es"])
def match_phrase(phrase:str='opened the box', eshost:str="es.corpusly.com:9200", cp:str='clec', topk:int=10): 	return requests.post(f"http://{eshost}/{cp}/_search/", json={"query": {  "match_phrase": { "snt": phrase }  } , "size": topk}).json()

@app.get("/es/newindex", tags=["es"])
def new_index(index:str='testidx', eshost:str="es.corpusly.com:9200"):
	from so import config
	requests.delete(f"http://{eshost}/{index}")
	return requests.put(f"http://{eshost}/{index}", json=config).text

@app.post("/es/addnew", tags=["es"])
def es_addnew(arr:dict={"essay_or_snts":"She has ready. It are ok. The justice delayed is justice denied. I plan to go swimming.", "rid":0, "uid":0}
		, index:str="exam", eshost:str="es.corpusly.com:9200", gecdskhost:str='gpu120.wrask.com:8180'):  
	''' assuming: index already exists, 2022.7.30 '''
	import en
	url = f"http://{eshost}/{index}"
	rid,uid = arr.get('rid',0), arr.get('uid',0)
	did		= f"rid-{rid}:uid-{uid}" # filename is a kind of uid 
	requests.post(f"http://{eshost}/{index}/_delete_by_query?conflicts=proceed", json={"query": { "match": { "did": did} }}).text

	dsk		= requests.post(f"http://{gecdskhost}/gecdsk", json=arr).json()
	for idx, mkf in enumerate(dsk['snt']):
		arrlex = mkf.get("meta",{}).get("lex_list",'').split()
		si = {}
		for k,v in mkf.get('feedback',{}).items(): 
			if v['cate'].startswith('e_') or v['cate'].startswith('w_'):
				si[ v['ibeg'] ] = v['cate'].split(".")[0]
		for i, w in enumerate(arrlex):
			requests.put(f"http://{eshost}/{index}/_doc/{did}:dsk-{idx * 1000 + i}", json ={"did":did,"i":idx * 1000 + i,  "type":"dsktag"
			, "labels": [si[i]] if i in si else [], "text":w, } )

	doc		= spacy.nlp(arr.get('essay_or_snts',''))
	snts	= [mkf.get('meta',{}).get('snt','') for mkf in dsk.get('snt',[])]
	arr.update({"type":"doc", "dsk":json.dumps(dsk), "json":json.dumps(doc.to_json()), "did": did, "rid":rid, "uid":uid, "sntnum":len(snts), "score":float(dsk.get('info',{}).get("final_score",0)), "snts": json.dumps(snts) })
	requests.put(f"http://{eshost}/{index}/_doc/{did}", json=arr )
	requests.put(f"http://{eshost}/{index}/_doc/{did}-dims", json=dict(dsk.get('doc',{}), **{"type":"dims", "did":did}))

	# add tag ,essay-level offset
	[ requests.put(f"http://{eshost}/{index}/_doc/{did}:ctag-NP-{doc[np.start].idx}", json={"did":did, "type":"ctag", "ctag": "NP", "start":doc[np.start].idx, "len":len(np.text), "chunk": np.text} ) for np in doc.noun_chunks if np.end - np.start > 1]
	[ requests.put(f"http://{eshost}/{index}/_doc/{did}:ctag-tok-{t.idx}", json ={"did":did, "type":"ctag", "ctag": t.pos_, "start":t.idx, "len":len(t.text), "chunk": t.text} ) for t in doc if t.pos_ not in ('X','PUNCT', 'SPACY')]
	[ requests.put(f"http://{eshost}/{index}/_doc/{did}:toktag-{t.idx}", json ={"did":did,"i":t.i,  "type":"toktag", "labels": [t.pos_] if t.pos_ in ('VERB','NOUN','ADJ','ADV','CCONJ') else [], "text":t.text, } ) for t in doc ]

	# 非谓语动词
	arr = [ {"did":did,"i":t.i,  "type":"vtag", "labels":[], "text":t.text} for t in doc]
	for name, start,end in matchers['vtov'](doc) :
		arr[start].update({"labels":['vtov'], "text": doc[start:end].text}) 
		for i in range(start+1, end): arr[i].update({"text":""})
	for name, start,end in matchers['vvbg'](doc) :
		arr[start].update({"labels":['vvbg'], "text": doc[start:end].text}) 
		for i in range(start+1, end): arr[i].update({"text":""})
	[ arr[t.i].update({"labels":['VBN']}) for t in doc if t.tag_ == 'VBN' ]
	[ requests.put(f"http://{eshost}/{index}/_doc/{did}:vtag-{t['i']}", json=t) for t in arr  if t['text'] ]

	for i, sent in enumerate(doc.sents):
		sdoc = sent.as_doc()
		labels = ['简单句' if len([t for t in sdoc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else '复杂句']
		if len([t for t in sdoc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0 : labels.append("复合句")
		requests.put(f"http://{eshost}/{index}/_doc/{did}:stag-{i}", json={"type":"stag", "i": i, "did": did, "rid":rid, "uid":uid, "id": f"{did}:stag-{i}", "text": sdoc.text, "labels": labels})
	return arr 

@app.post("/es/newdoc", tags=["es"])
def newdoc(arr:dict={"essay_or_snts":"The quick fox jumped over the lazy dog. The justice delayed is justice denied. She is very happy.", "rid":0, "uid":0}
		, index:str="shexam", eshost:str="es.corpusly.com:9200", gecdskhost:str='gpu120.wrask.com:8180' , refresh_index:bool=False ):  
	''' 2022.7.11 '''
	if not hasattr(newdoc, 'es'):
		from so import config
		from elasticsearch import Elasticsearch,helpers
		newdoc.es	= Elasticsearch([ f"http://{eshost}"])  
	if refresh_index: newdoc.es.indices.delete(index=index)
	if not newdoc.es.indices.exists(index=index): newdoc.es.indices.create(index=index, body=config) 

	from en.esjson import sntdoc_idsour #2022.7.10
	did		= f"rid-{arr.get('rid',0)}:uid-{arr.get('uid',0)}" # filename is a kind of uid 
	requests.post(f"http://{eshost}/{index}/_delete_by_query?conflicts=proceed", json={"query": { "match": { "did": did} }}).text

	dsk		= requests.post(f"http://{gecdskhost}/gecdsk", json=arr).json()
	snts	= [mkf.get('meta',{}).get('snt','') for mkf in dsk.get('snt',[])]
	arr.update({"type":"doc", "did": did, "sntnum":len(snts), "score":float(dsk.get('info',{}).get("final_score",0)), "snts": json.dumps(snts) })
	newdoc.es.index(index = index,  id = did, body = arr)
	newdoc.es.index(index = index,  id = f"{did}-dims", body = dict(dsk.get('doc',{}), **{"type":"dims", "did":did}) )

	for i,mkf in enumerate(dsk.get('snt',[])):  
		snt = mkf.get('meta',{}).get('snt','')
		doc = spacy.nlp(snt)
		[ newdoc.es.index(index = index,  id = f"{did}:" + ar["_id"], body = dict(ar['_source'], **{"did":did})) for ar in sntdoc_idsour( f"{did}:sid-{i})", snt, doc ) ]  
		[ newdoc.es.index(index = index,  id = f"{did}:sid-{i})-{v['ibeg']}", body = dict( v, **{"type":"cate", "did":did, "memo":snt, "src":f"{did}:sid-{i})"}))  for k,v in mkf.get('feedback',{}).items() if f"{did}:sid-{i})".startswith("e_") or v['cate'].startswith("w_") ]

	# add tag ,essay-level offset
	doc = spacy.nlp(arr.get('essay_or_snts',''))
	[ newdoc.es.index(index = index,  id = f"{did}:ctag-NP-{doc[np.start].idx}", body ={"did":did, "type":"ctag", "ctag": "NP", "start":doc[np.start].idx, "len":len(np.text), "chunk": np.text} ) for np in doc.noun_chunks if np.end - np.start > 1]
	[ newdoc.es.index(index = index,  id = f"{did}:ctag-tok-{t.idx}", body ={"did":did, "type":"ctag", "ctag": t.pos_, "start":t.idx, "len":len(t.text), "chunk": t.text} ) for t in doc if t.pos_ not in ('X','PUNCT', 'SPACY')]
	# clause 
	for v in [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT' ] : # non-root
		children = list(v.subtree)
		start = children[0].i  	#end = children[-1].i 
		cl = " ".join([c.text for c in v.subtree]) 	#spans.append ([doc[start].idx, doc[start].idx + len(cl), v.dep_])
		newdoc.es.index(index = index,  id = f"{did}:ctag-cl-{doc[start].idx})", body ={"did":did, "type":"ctag", "ctag": f"cl.{v.dep_}", "start":doc[start].idx, "len":len(cl), "chunk": cl} )
	# AP, VP 
	from en.terms import matchers
	for name, start,end in matchers['ap'](doc) :
		newdoc.es.index(index = index,  id = f"{did}:ctag-AP-{doc[start].idx}", body ={"did":did, "type":"ctag", "ctag": "AP", "start":doc[start].idx, "len":len(doc[start:end].text), "chunk": doc[start:end].text} )
	for name, start,end in matchers['vp'](doc) :
		newdoc.es.index(index = index,  id = f"{did}:ctag-VP-{doc[start].idx}", body ={"did":did, "type":"ctag", "ctag": "VP", "start":doc[start].idx, "len":len(doc[start:end].text), "chunk": doc[start:end].text} )
	# 非谓语动词
	for name, start,end in matchers['vtov'](doc) :
		newdoc.es.index(index = index,  id = f"{did}:ctag-vtov-{doc[start].idx}", body ={"did":did, "type":"ctag", "ctag": "vtov", "start":doc[start].idx, "len":len(doc[start:end].text), "chunk": doc[start:end].text} )
	for name, start,end in matchers['vvbg'](doc) :
		newdoc.es.index(index = index,  id = f"{did}:ctag-vvbg-{doc[start].idx}", body ={"did":did, "type":"ctag", "ctag": "vvbg", "start":doc[start].idx, "len":len(doc[start:end].text), "chunk": doc[start:end].text} )
	[newdoc.es.index(index = index,  id = f"{did}:ctag-VBN-{t.idx})", body ={"did":did, "type":"ctag", "ctag": "VBN", "start":t.idx, "len":len(t.text), "chunk": t.text} ) for t in doc if t.tag_ == 'VBN']

	for i, sent in enumerate(doc.sents):
		sdoc = sent.as_doc()
		stag = ["简单句" if len([t for t in sdoc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else "复杂句"] 
		if len([t for t in sdoc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0: stag.append("复合句")
		newdoc.es.index(index = index,  id = f"{did}:stag-{i}", body ={"did":did, "type":"stag", "stag": stag, "id": f"{did}:stag-{i})","src":f"{did}:sid-{i})", "start":doc[sent.start].idx, "len":len(sent.text), "chunk": sent.text} )
	return arr 

@app.post("/es/uploadfile/", tags=["es"])
async def create_upload_file(index:str="shexam", rid:int=0, file: UploadFile = File(...), refresh_index:bool = False):
	''' folder is the index name '''
	content = await file.read()
	return indexdoc({'essay_or_snts':content.decode().strip(),'rid':rid, 'uid':file.filename}, index=index, refresh_index=refresh_index)  

if __name__ == "__main__":   #uvicorn.run(app, host='0.0.0.0', port=80)
	#print ( rows(sum_query="select count(*) from gzjc where type='snt'") )
	print ( es_addnew())  #refresh_index=True
	uvicorn.run(app, host='0.0.0.0', port=80)

'''
POST /_sql
{
  "query":
  "select did, chunk, start, len, stag from shexam where type='stag' and did = 'rid-0:uid-0' "
}


@app.get('/es/xcnt/{cp}/{type}/{column}', tags=["es"])
def corpusly_xcnt( column:str='lex', cp:str='gzjc', type:str='tok', where:str="", order:str="order by cnt desc limit 10" ):
	#column:lex, cp:gzjc, type:tok, where:  and lem='book'  | JSONCompactColumns  
	# select lex,count(*) cnt from dic where type = 'tok' and lem= 'book' group by lex 
	query  = f"select {column}, count(*) cnt from {cp} where type = '{type}' {where} group by {column} {order}"
	res = requests.post(f"http://{requests.eshp}/_sql",json={"query": query}).json() 
	return [  { column: ar[0], "cnt": ar[1]} for ar in res['rows'] ] 

@app.get("/es/srcsnts", tags=["es"])
def corpus_srcsnts(query:str="select src from gzjc where type='tok' and lem='book' and pos='NOUN' limit 10",highlight:str='book', left_tag:str="<b>", right_tag:str="</b>"):  #, cp:str='gzjc'
	cp = query.split("where")[0].strip().split('from')[-1].strip()
	srclist = "','".join([ src for src, in rows(query)])
	return [{'snt':re.sub(rf"\b({highlight})\b", f"{left_tag}{highlight}{right_tag}", snt)} for snt, in rows(f"select snt from {cp} where type='snt' and src in ('{srclist}')")]

@app.get("/es/lempos/snts", tags=["es"])
def lempos_snts(cp:str='gzjc', lem:str='book', pos:str='VERB', topk:int=3, left_tag:str="<b>", right_tag:str="</b>"): 
	# "select snt from gzjc where type = 'snt' and kp = 'book_VERB' limit 2" , added 2022.6.24 
	query = f"select snt from {cp} where type = 'snt' and kp = '{lem}_{pos}' limit {topk}"
	return [{'snt':re.sub(rf"\b({lem})\b", f"{left_tag}{lem}{right_tag}", snt)} for snt, in rows(query)]	

@app.get("/es/trp/snts", tags=["es"])
def trp_snts(cp:str='gzjc', word:str='door', rel:str='~dobj_VERB_NOUN', cur:str='open',  topk:int=3): 
	query = f"select snt from {cp} where type = 'snt' and kp = '{rel[1:]}/{cur} {word}' limit {topk}" if rel.startswith('~') else f"select snt from {cp} where type = 'snt' and kp = '{rel}/{word} {cur}' limit {topk}"
	print (query, flush=True)
	return [{'snt':snt} for snt, in rows(query)]

	#if perc: 
	#	for col in df.columns:
	#		df[f"{col}_perc"] = round((df[col] / df[col].sum()) * 100, 2)
	#if topk > 0 : df = df.sort_values(df.columns[0], ascending=False)

#sntsum	= lambda cp: requests.post(f"http://{requests.eshp}/_sql",json={"query": f"select count(*) from {cp} where type ='snt'"}).json()['rows'][0][0]
'''