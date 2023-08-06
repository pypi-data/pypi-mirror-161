#2022.7.24 pip install mysqlclient
from uvirun import *
myhost,myport,mydb  = os.getenv("myhost", "lab.jukuu.com" if "Windows" in platform.system() else "172.17.0.1"), int(os.getenv("myport", 3307)) ,os.getenv("mydb", "kpsi")

@app.get('/kpsi/rows', tags=["kpsi"])
def rows(sql:str="show tables"):
	import pymysql
	if not hasattr(rows, 'conn') or not rows.conn.ping():
		rows.conn = pymysql.connect(host=myhost,port=myport,user='root',password='cikuutest!',db=mydb) #, defer_connect=True
	with rows.conn.cursor() as cursor: #pymysql.cursors.SSDictCursor
		cursor.execute(sql)
		res = cursor.fetchall()
	return res 

@app.get('/kpsi/snts', tags=["kpsi"], response_class=HTMLResponse)
def kpsi_snts(s:str="open:VERB:dobj:NOUN:door", cp:str='dic', hl_words:str="open,door", topk:int=10): 
	''' return HTML <ol><li> , 2022.7.24 '''
	from dic import lemma_lex
	sids = rows(f"select t from {cp} where s = '{s}' limit 1")
	if sids and len(sids) > 0 :
		sids = ",".join([str(sid) for sid in sids[0][0].split(',')[0:topk] ])
	snts = rows(f"select snt from {cp}_snt where sid in ({sids})")
	words = '|'.join([ '|'.join(list(lemma_lex.lemma_lex[w])) for w in hl_words.strip().split(',') if w in lemma_lex.lemma_lex])
	arr = [re.sub(rf'\b({words})\b', r'<font color="red">\g<0></font>', snt[0]) if words else snt[0] for snt in snts]
	html = "\n".join([f"<li>{snt}</li>" for snt in arr])
	return HTMLResponse(content=f"<ol>{html}</ol>")

def _walk( s, cp, children): 
	_rows = rows(f"select s,i,length(t) from {cp} where s like '{s}:%' and s not like '{s}:%:%'")
	for w,i, lent in _rows[0:5]: 
		if lent > 0: 
			children.append({"name": f"{w}[{i}]", "value": i} )
		else :
			a = {"name": f"{w}[{i}]", "children":[]}
			children.append( a ) 
			_walk(w, cp, a['children'] )

@app.get('/kpsi/flare', tags=["kpsi"])
def kpsi_flare(lem:str="open", cp:str="dic"):
	''' https://echarts.apache.org/examples/data/asset/data/flare.json '''
	i = rows(f"select i from {cp} where s ='LEM:{lem}' limit 1")[0][0]
	dic = { "name": f"{lem}[{i}]", "children":[] }
	for w, i in rows(f"select s,i from {cp} where s like '{lem}:%' and s not like '{lem}:%:%'"): 
		_walk(w, cp, dic["children"])
	return dic 

@app.get('/kpsi/kndata', tags=["kpsi"])
def kn_data(sumkey='knowledge:NOUN:~dobj', cps:str='clec', cpt:str='dic', slike:str="knowledge:NOUN:~dobj:VERB:%", tail:bool=False): 
	''' return (word, srccnt, tgtcnt, srcsum, tgtsum, keyness) '''
	try:
		clause = f"like '{slike}'" if '%' in slike else f" in ('" + "','".join(slike.strip().split(',')) + "')" # in ('consider:VERB:vtov','consider:VERB:vvbg')
		df = pd.DataFrame({cps: dict(rows(f"select s, i from {cps} where s {clause}")),
			cpt: dict(rows(f"select s, i from {cpt} where s {clause}"))}).fillna(0)
		df[f'{cps}_sum'] = rows(f"select i from {cps} where s ='{sumkey}' limit 1")[0][0]
		df[f'{cpt}_sum'] = rows(f"select i from {cpt} where s ='{sumkey}' limit 1")[0][0]
		df = df.sort_values(df.columns[0], ascending=False) #.astype(int)
		return [ {"index": index.split(':')[-1] if tail else index
		,cps:int(row[cps]),f'Σ{cps}':int(row[f'{cps}_sum'])
		,cpt:int(row[cpt]),f'Σ{cpt}':int(row[f'{cpt}_sum'])
		,'keyness':likelihood(row[cps],row[cpt],row[f'{cps}_sum'],row[f'{cpt}_sum'])}  for index, row in df.iterrows()] 
	except Exception as e:
		print("kn_data ex:", e) 
		return []

@app.post('/kpsi/kntrp', tags=["kpsi"])
def kntrp(sarr:list=['open:VERB:dobj:NOUN:door','close:VERB:dobj:NOUN:door','knowledge:NOUN:~dobj:VERB:learn'], cps:str='clec', cpt:str='gzjc'): 
	''' [{'index': 'knowledge:NOUN:~dobj:VERB:learn', '#clec': 146, 'Σclec': 563, '#gzjc': 0, 'Σgzjc': 6, 'keyness': 3.1}, {'index': 'open:VERB:dobj:NOUN:door', '#clec': 31, 'Σclec': 102, '#gzjc': 1, 'Σgzjc': 22, 'keyness': 6.67}, {'index': 'close:VERB:dobj:NOUN:door', '#clec': 11, 'Σclec': 33, '#gzjc': 1, 'Σgzjc': 6, 'keyness': 0.53}] '''
	try:
		sarr	= [s.strip() for s in sarr if not "'" in s]
		clause	= f" in ('" + "','".join(sarr) + "')" 
		sicps	= dict(rows(f"select s, i from {cps} where s {clause}"))
		sicpt	= dict(rows(f"select s, i from {cpt} where s {clause}"))

		sumarr	= {s[0:s.rfind(':')]: s for s in sarr} #open:VERB:dobj:NOUN:door => open:VERB:dobj:NOUN
		sclause	= f" in ('" + "','".join(sumarr) + "')" 
		sumcps	= dict(rows(f"select s, i from {cps} where s {sclause}"))
		sumcpt	= dict(rows(f"select s, i from {cpt} where s {sclause}"))
		
		df = pd.DataFrame({cps: sicps, cpt: sicpt, f'{cps}_sum': { sumarr.get(s,s): i  for s,i in sumcps.items()}, f'{cpt}_sum': { sumarr.get(s,s): i  for s,i in sumcpt.items()}  }).fillna(0)
		#df = df.sort_values(df.columns[0], ascending=False) 
		return [ {"index": index
		,cps:int(row[cps]),f'Σ{cps}':int(row[f'{cps}_sum'])
		,cpt:int(row[cpt]),f'Σ{cpt}':int(row[f'{cpt}_sum'])
		,'keyness':likelihood(row[cps],row[cpt],row[f'{cps}_sum'],row[f'{cpt}_sum'])}  for index, row in df.iterrows()] 
	except Exception as e:
		print("kntrp ex:", e) 
		return []

if __name__ == '__main__':
	#print (kpsi_flare(), flush=True) 
	uvicorn.run(app, host='0.0.0.0', port=80)

'''

print (kntrp([
  "open:VERB:dobj:NOUN:door",
  "close:VERB:dobj:NOUN:door",
  "knowledge:NOUN:~dobj:VERB:learn",
"attach:VERB:nsubj:NOUN:company",
"importance:NOUN:amod:ADJ:equal",
"attach:VERB:dobj:NOUN:importance",
"skill:NOUN:amod:ADJ:social",
"qualification:NOUN:amod:ADJ:academic",
"hire:VERB:advmod:ADV:when",
"employee:NOUN:amod:ADJ:new",
"hire:VERB:dobj:NOUN:employee",
"be:AUX:nsubj:NOUN:education"]), flush=True)

@app.get('/kpsi/si', tags=["kpsi"])
def si(sql,asdic:bool=True): return { s:int(i) for s,i in rows(sql)} if asdic else [ (s,int(i)) for s,i in rows(sql)]

import io
from starlette.responses import StreamingResponse
app = FastAPI()
@app.post("/vector_image")
def image_endpoint(*, vector):
    # Returns a cv2 image array from the document vector
    cv2img = my_function(vector)
    res, im_png = cv2.imencode(".png", cv2img)
    return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")

mysqldump -uroot -pcikuutest! --port 3307 --host=172.17.0.1 kpsi dic dic_snt --result-file=dic.sql

@app.get('/kpsi/flare1', tags=["kpsi"])
def kpsi_flare1(lem:str="open", cp:str="dic"):
	# https://echarts.apache.org/examples/data/asset/data/flare.json
	i = rows(f"select i from {cp} where s ='LEM:{lem}' limit 1")[0][0]
	dic = { "name": f"{lem}[{i}]", "children":[] }
	for w, i in rows(f"select s,i from {cp} where s like '{lem}:%' and s not like '{lem}:%:%'"): #select s,i from {cp} where s in ('{lem}:VERB','{lem}:NOUN','{lem}:ADJ','{lem}:ADV')
		a = {"name": f"{w}[{i}]", "children":[]}
		for s,i in rows(f"select s,i from {cp} where s like '{w}:%' and s not like '{w}:%:%'"):
			b = {"name": f"{s}[{i}]", "value": i}  #"children":[]
			a["children"].append( b ) 
		dic["children"].append( a ) 
	return dic 


'''