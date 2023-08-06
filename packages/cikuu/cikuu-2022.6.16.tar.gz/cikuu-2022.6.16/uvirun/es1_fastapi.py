# 2022.6.30 cp from uvicorn corpusly-19200:app --host 0.0.0.0 --port 19200 --reload
from uvirun import *
from util import likelihood

from so import *
requests.eshost	= os.getenv("eshost", "es.corpusly.com" if "Windows" in platform.system() else "172.17.0.1")
requests.esport	= int(os.getenv("esport", 9200))
requests.es		= Elasticsearch([ f"http://{requests.eshost}:{requests.esport}" ])   # overwrite

# to be removed later, when cikuu is updated
kwic	= lambda cp, w, topk=3 : [ re.sub(rf"\b({w})\b", f"<b>{w}</b>", row[0]) for row in rows(f"select snt from {cp} where type = 'snt' and match (snt, '{w}') limit {topk}")]

@app.get('/es/xcnt/{cp}/{type}/{column}')
def es_xcnt( column:str='lex', cp:str='dic', type:str='tok', where:str="", order:str="order by cnt desc limit 10",  name:str="es.corpusly.com:9200" ):
	''' where:  and lem='book'  | JSONCompactColumns
	* select lex,count(*) cnt from dic where type = 'tok' and lem= 'book' group by lex '''
	query  = f"select {column}, count(*) cnt from {cp} where type = '{type}' {where} group by {column} {order}"
	res = requests.post(f"http://{name}/_sql",json={"query": query}).json() 
	return [  { column: ar[0], "cnt": ar[1]} for ar in res['rows'] ] 

@app.get('/es/sqlrows')
def sqlrows(query="select lem, count(*) cnt  from gzjc where type = 'tok' and pos != 'PUNCT' group by lem order by cnt desc limit 10", perc_column:str=None):
	''' perc_column: cnt  
	# select gov, count(*) cnt from gzjc where type = 'tok' and lem='door' and pos='NOUN' and dep='dobj' group by gov
	# select lem, count(*) cnt from gzjc where type = 'tok' and gov='open_VERB' and pos='NOUN' and dep='dobj' group by lem
	'''
	res = requests.post(f"http://{requests.eshost}:{requests.esport}/_sql",json={"query": query}).json() 
	arr = [  dict(zip([ ar['name'] for ar in res['columns'] ] , ar)) for ar in res['rows'] ] 
	if perc_column:  
		sump = sum([ ar[perc_column] for ar in arr]) + 0.0001
		[ ar.update({'perc': round(ar[perc_column] / sump, 4) }) for ar in arr]
	return arr

@app.post('/es/sqlrows')
def es_sqlrows_post(querys:list=["show tables","select lem, count(*) cnt  from gzjc where type = 'tok' and pos != 'PUNCT' group by lem order by cnt desc limit 10"], asdic:bool=True):
	return {query: sqlrows(query) for query in querys} if asdic else [ sqlrows(query) for query in querys ]

@app.post('/es/rows')
def named_rows(arr:dict={'query':"select lem, count(*) cnt from dic where type='tok' and  tag='VBG' group by lem order by cnt desc ", 'columns':["lem", "tagcnt"]}):
	''' 2022.6.21 '''
	return [  dict(zip(arr['columns'], ar)) for ar in rows( arr.get('query', "") ) ] 

@app.get('/es/termcnt')
def es_query_termcnt(cps:str="clec,gzjc", query:str="select gov, count(*) cnt from __0__ where type = 'tok' and lem='door' and pos='NOUN' and dep='dobj' group by gov", topk:int=10 ):
	''' added 2022.6.19 '''
	map = defaultdict(dict)
	for cp in cps.strip().split(','): 
		sql = query.replace("__0__", cp ) 
		for row in rows(sql): # assume the first one is the key 
			for i in range(1, len(row)): 
				map[ row[0]][ f"{cp}_{i}" if i > 1 else cp] = row[i]
	df = pd.DataFrame(map).fillna(0).transpose()
	for col in df.columns:
		df[f"{col}_perc"] = round((df[col] / df[col].sum()) * 100, 2)
	if topk > 0 : df = df.sort_values(df.columns[0], ascending=False)
	arr = [ dict(dict(row), **{"term": index} ) for index, row in df.iterrows()] 
	return arr[0:topk] if topk > 0  else arr 

@app.get("/es/indexlist/")
def corpus_indexlist(verbose:bool=False):
	names =  [ar['name'] for ar in sqlrows("show tables")  if not ar['name'].startswith(".") and ar['type'] == 'TABLE' and ar['kind'] == 'INDEX'] # {"catalog":"elasticsearch","name": ".apm-custom-link", "type": "TABLE",    "kind": "INDEX"  },
	return [ dict( dict(rows(f"select type, count(*) cnt from {name} group by type")), **{"name":name} ) for name in names] if verbose else names

@app.get("/es/stats")
def corpus_stats(names:str=None, types:str="doc,snt,np,tok,trp,vp"):
	''' doc,snt,np,tok,simple_sent,vtov,vvbg,vp, added 2022.5.21 '''
	names = name.strip().split(',') if names else [ar['name'] for ar in sqlrows("show tables")  if not ar['name'].startswith(".") and ar['type'] == 'TABLE' and ar['kind'] == 'INDEX']
	types = types.replace(",", "','")
	return [ dict( dict(rows(f"select type, count(*) cnt from {name} where type in ('{types}') group by type")), **{"name":name} ) for name in names]

@app.post("/es/uploadfile/")
async def create_upload_file(index:str="testidx", file: UploadFile = File(...), refresh_index:bool = False):
	''' folder is the index name '''
	content = await file.read()
	return indexdoc({'body':content.decode().strip(), 'index':index, 'filename':file.filename}, idxname=index, refresh_index=refresh_index)  

@app.post('/es/search') 
def es_search(query:dict={"match_all": {}}, index:str="testidx", size:int=10):  
	''' {"match": { "type":"snt"} } '''
	return requests.es.search(index=index,  query=query, size=size)

@app.get("/es/kwic")
def corpus_kwic(cp:str='dic', w:str="opened", topk:int=10, left_tag:str="<b>", right_tag:str="</b>"): # expected_tc:int=15,
	''' search snt using word,  | select snt,postag, tc from gzjc where type = 'snt' and match(snt, 'books') | 2022.6.19 '''
	return [ {"snt": re.sub(rf"\b({w})\b", f"{left_tag}{w}{right_tag}", snt), "tc": tc } for snt, postag, tc in rows(f"select snt, postag, tc from {cp.strip().split(',')[0]} where type = 'snt' and match (snt, '{w}') limit {topk}")]

@app.get("/es/mf")
def corpus_mf(cps:str="gzjc,clec", w:str="considered", topk:int=3, with_snt:bool=False):
	dic =  {cp: round(1000000 * phrase_num(w, cp) / (sntnum(cp)+0.1), 2 ) for cp in cps.strip().split(',') }
	return [ {"cp":cp, "mf":mf, "snts": json.dumps(kwic(cp, w, topk)) } for cp,mf in dic.items()] if with_snt else [ {"cp":cp, "mf":mf } for cp,mf in dic.items()]

@app.get("/es/srcsnts")
def corpus_srcsnts(query:str="select src from gzjc where type='tok' and lem='book' and pos='NOUN' limit 10",highlight:str='book', left_tag:str="<b>", right_tag:str="</b>"):  #, cp:str='gzjc'
	''' '''
	cp = query.split("where")[0].strip().split('from')[-1].strip()
	srclist = "','".join([ src for src, in rows(query)])
	return [{'snt':re.sub(rf"\b({highlight})\b", f"{left_tag}{highlight}{right_tag}", snt)} for snt, in rows(f"select snt from {cp} where type='snt' and src in ('{srclist}')")]

@app.get("/es/lempos/snts")
def lempos_snts(cp:str='gzjc', lem:str='book', pos:str='VERB', topk:int=3, left_tag:str="<b>", right_tag:str="</b>"): 
	''' "select snt from gzjc where type = 'snt' and kp = 'book_VERB' limit 2" , added 2022.6.24 '''
	query = f"select snt from {cp} where type = 'snt' and kp = '{lem}_{pos}' limit {topk}"
	return [{'snt':re.sub(rf"\b({lem})\b", f"{left_tag}{lem}{right_tag}", snt)} for snt, in rows(query)]	

@app.get("/es/trp/snts")
def trp_snts(cp:str='gzjc', word:str='door', rel:str='~dobj_VERB_NOUN', cur:str='open',  topk:int=3): 
	query = f"select snt from {cp} where type = 'snt' and kp = '{rel[1:]}/{cur} {word}' limit {topk}" if rel.startswith('~') else f"select snt from {cp} where type = 'snt' and kp = '{rel}/{word} {cur}' limit {topk}"
	print (query, flush=True)
	return [{'snt':snt} for snt, in rows(query)]

@app.get("/es/match_phrase")
def corpus_match_phrase(phrase:str='opened the box', cp:str='clec', topk:int=10):  return match_phrase(phrase, cp, topk)
@app.get("/es/match_phrase_num")
def corpus_phrase_num(phrase:str='opened the box', cp:str='clec', topk:int=10): return phrase_num(phrase, cp, topk)["hits"]["total"]["value"]

@app.get("/es/nearby")
def corpus_nearby(lem:str="environment", corpus:str='spin', poslist:str="'NOUN','ADJ','VERB'", topk:int=20):
	''' words nearby '''
	rows = requests.post(f"http://{requests.eshost}:{requests.esport}/_sql",json={"query": f"select src from {corpus} where type = 'tok' and lem = '{lem}'"}).json()['rows']
	snts = "','".join([row[0] for row in rows])
	res = requests.post(f"http://{requests.eshost}:{requests.esport}/_sql",json={"query": f"select lem from {corpus} where type = 'tok'  and pos in ({poslist}) and src in ('{snts}')" }).json()['rows']
	si = Counter() 
	[si.update({row[0]:1}) for row in res if row[0] != lem and not row[0] in spacy.stoplist ]
	return Counter({ s:i * spacy.wordidf.get(s, 0) for s,i in si.items()}).most_common(topk)

@app.get('/es/hybchunk')
def corpus_hybchunk(hyb:str='the _NNS of', index:str='gzjc', size:int=-1, topk:int=10):
	''' the _NNS of -> {the books of: 13, the doors of: 7} , added 2021.10.13 '''
	return hybchunk(hyb, index, size, topk)
@app.get('/es/truncate_index')
def truncate_index(index:str='testidx'): 	return requests.post(f"http://{requests.eshost}:{requests.esport}/{index}/_delete_by_query?conflicts=proceed", json={"query": { "match_all": {} }}).json()
@app.get('/es/delete_file') 
def delete_file(filename:str, index:str='testidx'): 	return requests.post(f"http://{requests.eshost}:{requests.esport}/{index}/_delete_by_query?conflicts=proceed", json={"query": { "match": { "filename": filename} }}).json()

@app.get('/es/dualsql_keyness')
def text_keyness(sql1:str= "select lem,  count(*) from inau where type = 'tok' and pos='VERB'  group by lem", sql2:str="select lem,  count(*) from gzjc where type = 'tok' and pos='VERB' group by lem", threshold:float=0.0): 
	''' keyness of sql1, sql2, added 2021.10.24  '''
	src = dict(requests.post(f"http://{requests.eshost}:{requests.esport}/_sql",json={"query": sql1}).json()['rows'])
	tgt = dict(requests.post(f"http://{requests.eshost}:{requests.esport}/_sql",json={"query": sql2}).json()['rows'])
	return [ {"word": word, 'cnt1':c1, 'cnt2':c2, 'sum1':r1, 'sum2':r2, 'keyness':keyness} for word, c1, c2, r1, r2, keyness in dualarr_keyness(src, tgt, threshold) ]

@app.get('/es/init_index')
def init_index(idxname:str='testidx'):  requests.es.newindex(idxname)

if __name__ == "__main__":   #uvicorn.run(app, host='0.0.0.0', port=80)
	print (es_xcnt())	
	#print(requests.post(f"http://{name}/_sql",json={"query": query}).json() )