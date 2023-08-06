# 2022-7-9  depart from so/__main__.py 
import json,fire,sys, os, hashlib ,time , requests
from collections import Counter , defaultdict
from elasticsearch import Elasticsearch,helpers

def esjson_load(infile, batch=1000000, refresh:bool=True, eshost='127.0.0.1',esport=9200): 
	''' python3 -m so load gzjc.esjson '''
	es	  = Elasticsearch([ f"http://{eshost}:{esport}" ])  
	if not idxname : idxname = infile.split('.')[0]
	print(">>started: " , infile, idxname, flush=True )
	if refresh: self.init(idxname) 
	actions=[]
	for line in readline(infile): 
		try:
			arr = json.loads(line)  #arr.update({'_op_type':'index', '_index':idxname,}) 
			actions.append( {'_op_type':'index', '_index':idxname, '_id': arr.get('_id',None), '_source': arr.get('_source',{}) } )
			if len(actions) >= batch: 
				helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
				print ( actions[-1], flush=True)
				actions = []
		except Exception as e:
			print("ex:", e)	
	if actions : helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
	print(">>finished " , infile, idxname )

if __name__ == '__main__':
	fire.Fire(esjson_load)

'''
{"_index": "gzjc", "_type": "_doc", "_id": "2897-stype", "_source": {"src": 2897, "tag": "simple_snt", "type": "stype"}}
import warnings
warnings.filterwarnings("ignore")

'''