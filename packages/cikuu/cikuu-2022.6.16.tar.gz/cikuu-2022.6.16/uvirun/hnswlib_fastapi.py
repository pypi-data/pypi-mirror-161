# 2022.7.20  # 2022.2.5  https://github.com/nmslib/hnswlib/
from uvirun import *

@app.get('/hnswlib/vecso')
def vecso(snt:str="I am too tired to move on.", topk:int=10, name:str='dic'): 
	''' return [{'sid':, 'snt':, 'dis':}], JSONEachRow format, 2022.6.26	'''
	import hnswlib, json, sqlite3
	from sentence_transformers import SentenceTransformer, util
	if not hasattr(vecso, 'model'): vecso.model = SentenceTransformer('/data/model/sentence-transformers/all-MiniLM-L6-v2')
	vecs = vecso.model.encode([snt])  # 384 dim

	if not hasattr(vecso, name):  
		setattr(vecso, f"conn_{name}",  sqlite3.connect(f"/data/model/hnswlib/{name}.sntdb", check_same_thread=False) ) 
		conn = getattr(vecso, f"conn_{name}")
		conn.execute('PRAGMA synchronous=OFF')
		num  = list(conn.execute(f"select count(*) from snt" ))[0][0]
		print ("num:", num, flush=True)
		setattr(vecso, name , hnswlib.Index(space='l2', dim=384) )  # the space can be changed - keeps the data, alters the distance function.
		getattr(vecso, name).load_index(f"/data/model/hnswlib/{name}.hnswlib", max_elements = num)

	p = getattr(vecso, name) 
	labels, distances = p.knn_query(vecs, k=topk)
	maps = [{ row[0]: row[1] for row in getattr(vecso, f"conn_{name}").execute(f"select rowid, snt from snt where rowid in ({','.join([str(s) for s in label.tolist()])})" )} for label in labels] 	#list(conn.execute(f"select rowid, snt from snt where rowid in (6561,3843)" ))
	return [ [ {"sid":l, "snt": map.get(l,''), "distance":d } for l, d in zip(label.tolist(), distance.tolist()) ] for label,distance,map in zip(labels, distances, maps) ][0]

@app.get('/hnswlib', response_class=HTMLResponse)
def vecso_html(snt:str="I am too tired to move on.", topk:int=10, name:str='dic'): 
	''' return HTML <ol><li> , 2022.7.22 '''
	rows = vecso(snt, topk, name) 
	snts = "\n".join([f"<li>{row.get('snt','')}</li>" for row in rows])
	return HTMLResponse(content=f"<ol>{snts}</ol>")

@app.post('/hnswlib/vecso')
def vecso_post(snts:list=["I am too tired to move on.", "I love you."], topk:int=10, name:str='dic'):
	''' batch mode '''
	return {snt: vecso(snt, topk=topk , name=name) for snt in snts }

if __name__ == '__main__': 
	print (vecso_html())

'''
<ol>
  <li>Coffee</li>
  <li>Tea</li>
  <li>Milk</li>
</ol>
'''